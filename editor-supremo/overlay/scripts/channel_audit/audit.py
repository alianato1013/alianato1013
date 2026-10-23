#!/usr/bin/env python3
"""Script <-> visual audit for the channel-documentary pipeline (Editor Supremo).

Two subcommands:

  build   Pair every narrated sentence with every visual on screen while it is
          spoken, and write an audit sheet the agent grades by LOOKING at each frame.

            python scripts/channel_audit/audit.py build \
                --project projects/<project-id> --mode storyboard
            python scripts/channel_audit/audit.py build \
                --project projects/<project-id> --mode render \
                --video projects/<project-id>/renders/final.mp4 \
                --words projects/<project-id>/audit/render/final_transcript.json

  lock    Hash the narration of the user's script (markers removed) and check that the
          script artifact still matches it:
            python scripts/channel_audit/audit.py lock \
                --source projects/<project-id>/inputs/script_source.md --project projects/<project-id>

  verify  Check the agent's grades against the bible's minimum score and write
          audit_report.json (status PASS or FAIL). Exit code 1 on FAIL.

            python scripts/channel_audit/audit.py verify \
                --project projects/<project-id> --mode storyboard --min-score 4

Outputs live in projects/<project-id>/audit/<mode>/:
  audit_sheet.json      one row per (sentence x visual) pair
  grades_template.json  rows to fill: score 1-5, verdict, reason, fix
  contact_sheet.html    side-by-side view of each line and its frame
  frames/               extracted frames (render mode, and video clips in storyboard mode)
  audit_report.json     written by `verify`

Timing sources, best first:
  1. --words: a transcript JSON with word timestamps on the video timeline
     (OpenMontage transcriber output: {"word_timestamps": [{"word","start","end"}]}).
  2. The narration segments in edit_decisions.audio.narration.segments.
  3. The script section start/end seconds.
Within a section without word timings, sentence times are proportional to word count.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

MARKER_LINE = re.compile(r"^\s*\[[^\]]*\]\s*$")
INLINE_TAG = re.compile(r"\[(?:VISUAL|VERIFY|SRC|BRAND CARD|VERIFY QUOTE)[^\]]*\]", re.IGNORECASE)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])[\"”’)\]]*\s+(?=[\"“‘(\[]?[A-Z0-9#¿¡])")
TOKEN = re.compile(r"[a-z0-9']+")
MIN_OVERLAP_SECONDS = 0.5
GRAPHIC_TYPES = {
    "text_card", "hero_title", "stat_card", "callout", "comparison", "bar_chart",
    "line_chart", "pie_chart", "kpi_grid", "progress_bar",
}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".m4v", ".avi"}


# ---------------------------------------------------------------- artifacts

def load_artifact(project: Path, name: str, stage: str) -> Optional[dict]:
    """Return an artifact from its checkpoint, falling back to artifacts/<name>.json."""
    checkpoint = project / f"checkpoint_{stage}.json"
    if checkpoint.exists():
        data = json.loads(checkpoint.read_text(encoding="utf-8"))
        artifact = (data.get("artifacts") or {}).get(name)
        if artifact:
            return artifact
    loose = project / "artifacts" / f"{name}.json"
    if loose.exists():
        return json.loads(loose.read_text(encoding="utf-8"))
    return None


def require(artifact: Optional[dict], name: str) -> dict:
    if not artifact:
        sys.exit(f"[audit] missing artifact '{name}' (checkpoint or artifacts/{name}.json)")
    return artifact


# ---------------------------------------------------------------- text

def narration_lines(text: str) -> str:
    kept = [line for line in text.splitlines() if not MARKER_LINE.match(line)]
    return INLINE_TAG.sub("", " ".join(kept))


def split_sentences(text: str) -> list[str]:
    clean = re.sub(r"\s+", " ", narration_lines(text)).strip()
    if not clean:
        return []
    return [s.strip() for s in SENTENCE_SPLIT.split(clean) if s.strip()]


def tokens(text: str) -> list[str]:
    return TOKEN.findall(text.lower().replace("’", "'"))


def narration_sha256(sections: list[dict]) -> str:
    joined = " ".join(re.sub(r"\s+", " ", narration_lines(s.get("text", ""))).strip() for s in sections)
    return hashlib.sha256(re.sub(r"\s+", " ", joined).strip().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- timing

def section_windows(script: dict, edit: dict, manifest: dict) -> dict[str, tuple[float, float]]:
    """Timeline window per script section: narration segments first, script timing second."""
    windows = {s["id"]: (float(s["start_seconds"]), float(s["end_seconds"])) for s in script["sections"]}
    assets = {a["id"]: a for a in manifest.get("assets", [])}
    segments = (((edit.get("audio") or {}).get("narration") or {}).get("segments")) or []
    for seg in segments:
        asset = assets.get(seg.get("asset_id"), {})
        section_id = ((asset.get("voice_performance") or {}).get("source_section_id")
                      or asset.get("scene_id"))
        if section_id not in windows:
            continue
        start = float(seg["start_seconds"])
        end = seg.get("end_seconds")
        if end is None and asset.get("duration_seconds"):
            end = start + float(asset["duration_seconds"])
        if end is not None:
            windows[section_id] = (start, float(end))
    return windows


def proportional_times(sentences: list[str], start: float, end: float) -> list[tuple[float, float]]:
    counts = [max(1, len(tokens(s))) for s in sentences]
    total = sum(counts)
    out, cursor = [], start
    for count in counts:
        span = (end - start) * count / total
        out.append((cursor, cursor + span))
        cursor += span
    return out


def align_to_words(rows: list[dict], words: list[dict]) -> int:
    """Greedy sequential alignment of sentence tokens to transcript words. Returns rows aligned."""
    wtok = [(tokens(w.get("word", "")), float(w["start"]), float(w["end"])) for w in words]
    flat = [(t, s, e) for toks, s, e in wtok for t in toks]
    pointer, aligned = 0, 0
    for row in rows:
        stoks = tokens(row["text"])
        if not stoks:
            continue
        hits: list[tuple[float, float]] = []
        p = pointer
        for tok in stoks:
            for look in range(p, min(p + 8, len(flat))):
                if flat[look][0] == tok:
                    hits.append((flat[look][1], flat[look][2]))
                    p = look + 1
                    break
        if hits and len(hits) / len(stoks) >= 0.6:
            row["t_start"], row["t_end"] = hits[0][0], hits[-1][1]
            row["timing_source"] = "words"
            pointer = p
            aligned += 1
    return aligned


# ---------------------------------------------------------------- visuals

def resolve_asset(source: str, assets: dict[str, dict], project: Path) -> tuple[Optional[str], dict]:
    if source in assets:
        asset = assets[source]
        return asset.get("path"), asset
    candidate = Path(source)
    for path in (candidate, project / candidate, project.parent.parent / candidate):
        if path.exists():
            return str(path), {}
    return None, {}


def abs_path(path: Optional[str], project: Path) -> Optional[Path]:
    if not path:
        return None
    for candidate in (Path(path), project / path, project.parent.parent / path):
        if candidate.exists():
            return candidate.resolve()
    return None


def extract_frame(video: Path, seconds: float, out: Path) -> bool:
    if not shutil.which("ffmpeg"):
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0.0, seconds):.3f}", "-i", str(video),
           "-frames:v", "1", "-vf", "scale=960:-2", str(out)]
    return subprocess.run(cmd, check=False).returncode == 0 and out.exists()


# ---------------------------------------------------------------- build

def build(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    out_dir = project / "audit" / args.mode
    frames_dir = out_dir / "frames"
    out_dir.mkdir(parents=True, exist_ok=True)

    script = require(load_artifact(project, "script", "script"), "script")
    edit = require(load_artifact(project, "edit_decisions", "edit"), "edit_decisions")
    manifest = require(load_artifact(project, "asset_manifest", "assets"), "asset_manifest")
    scene_plan = load_artifact(project, "scene_plan", "scene_plan") or {"scenes": []}

    lock = (script.get("metadata") or {}).get("script_lock") or {}
    current_hash = narration_sha256(script["sections"])
    lock_ok = (lock.get("narration_sha256") == current_hash) if lock.get("narration_sha256") else None

    assets = {a["id"]: a for a in manifest.get("assets", [])}
    scenes = {s["id"]: s for s in scene_plan.get("scenes", [])}
    windows = section_windows(script, edit, manifest)

    rows: list[dict] = []
    for section in script["sections"]:
        sentences = split_sentences(section.get("text", ""))
        start, end = windows[section["id"]]
        for (t0, t1), text in zip(proportional_times(sentences, start, end), sentences):
            rows.append({"section_id": section["id"], "section_label": section.get("label", ""),
                         "text": text, "t_start": round(t0, 3), "t_end": round(t1, 3),
                         "timing_source": "proportional"})

    if args.words:
        data = json.loads(Path(args.words).read_text(encoding="utf-8"))
        words = data.get("word_timestamps") or [w for seg in data.get("segments", []) for w in seg.get("words", [])]
        aligned = align_to_words(rows, words)
        print(f"[audit] aligned {aligned}/{len(rows)} sentences to word timestamps")

    cuts = sorted(edit.get("cuts", []), key=lambda c: float(c["in_seconds"]))
    primary = [c for c in cuts if (c.get("layer") in (None, "", "primary"))]
    overlays = edit.get("overlays", []) or []

    video = abs_path(args.video, project) if args.video else None
    if args.mode == "render" and not video:
        sys.exit("[audit] render mode needs --video pointing at the rendered file")

    sheet: list[dict] = []
    for index, row in enumerate(rows, start=1):
        t0, t1 = row["t_start"], row["t_end"]
        overlapping = [c for c in primary
                       if min(t1, float(c["out_seconds"])) - max(t0, float(c["in_seconds"])) >= MIN_OVERLAP_SECONDS
                       or (float(c["in_seconds"]) <= (t0 + t1) / 2 < float(c["out_seconds"]))]
        if not overlapping:
            sheet.append({**row, "row_id": f"L{index:04d}-NOVISUAL", "line_index": index, "cut_id": None,
                          "visual_kind": "missing", "frame_path": None, "flags": ["NO_VISUAL"]})
            continue
        covered = sum(max(0.0, min(t1, float(c["out_seconds"])) - max(t0, float(c["in_seconds"]))) for c in overlapping)
        if (t1 - t0) - covered > MIN_OVERLAP_SECONDS:
            sheet.append({**row, "row_id": f"L{index:04d}-GAP", "line_index": index, "cut_id": None,
                          "visual_kind": "missing", "frame_path": None,
                          "flags": [f"GAP_{(t1 - t0) - covered:.1f}s_WITHOUT_PRIMARY_VISUAL"]})
        seen = set()
        for part, cut in enumerate(overlapping, start=1):
            if cut["id"] in seen:
                continue
            seen.add(cut["id"])
            c0, c1 = float(cut["in_seconds"]), float(cut["out_seconds"])
            mid = (max(t0, c0) + min(t1, c1)) / 2
            path, asset = resolve_asset(str(cut.get("source", "")), assets, project)
            scene = scenes.get(asset.get("scene_id", ""), {})
            kind = "graphic" if cut.get("type") in GRAPHIC_TYPES else "media"
            frame: Optional[Path] = None
            flags: list[str] = []
            row_id = f"L{index:04d}-V{part}"
            if args.mode == "render":
                frame = frames_dir / f"{row_id}.jpg"
                if not extract_frame(video, mid, frame):
                    frame, flags = None, ["FRAME_EXTRACTION_FAILED"]
            elif kind == "media":
                source_file = abs_path(path, project)
                if source_file is None:
                    flags.append("ASSET_FILE_MISSING")
                elif source_file.suffix.lower() in VIDEO_EXT:
                    frame = frames_dir / f"{row_id}.jpg"
                    offset = float(cut.get("source_in_seconds") or 0) + (mid - c0) * float(cut.get("speed") or 1)
                    if not extract_frame(source_file, offset, frame):
                        frame, flags = None, ["FRAME_EXTRACTION_FAILED"]
                else:
                    frame = source_file
            on_screen_overlays = [o.get("asset_id") for o in overlays
                                  if float(o["start_seconds"]) <= mid < float(o["end_seconds"])]
            sheet.append({
                **row, "row_id": row_id, "line_index": index, "cut_id": cut["id"],
                "cut_window": [c0, c1], "frame_time": round(mid, 3), "visual_kind": kind,
                "cut_type": cut.get("type"), "graphic_text": cut.get("text") or cut.get("stat") or cut.get("title"),
                "asset_id": asset.get("id") or cut.get("source"), "asset_path": path,
                "asset_prompt": asset.get("prompt"), "asset_license": asset.get("license"),
                "asset_source_url": asset.get("original_url"),
                "scene_description": scene.get("description"),
                "overlays_on_screen": on_screen_overlays,
                "frame_path": str(frame) if frame else None, "flags": flags,
            })

    meta = {"mode": args.mode, "project": str(project), "rows": len(sheet), "sentences": len(rows),
            "script_lock_ok": lock_ok, "narration_sha256": current_hash, "video": str(video) if video else None}
    (out_dir / "audit_sheet.json").write_text(json.dumps({"meta": meta, "rows": sheet}, indent=2), encoding="utf-8")
    template = [{"row_id": r["row_id"], "score": None, "verdict": None, "hard_fail": [], "reason": "", "fix": ""}
                for r in sheet]
    template_path = out_dir / "grades_template.json"
    template_path.write_text(json.dumps(template, indent=2), encoding="utf-8")
    write_contact_sheet(out_dir, sheet, meta)

    missing = sum(1 for r in sheet if r["flags"])
    print(f"[audit] {args.mode}: {len(rows)} sentences -> {len(sheet)} rows; {missing} rows with flags")
    if lock_ok is False:
        print("[audit] CRITICAL: narration no longer matches the locked script hash")
    print(f"[audit] sheet: {out_dir / 'audit_sheet.json'}")
    print(f"[audit] grade every row into: {out_dir / 'grades.json'} (copy of grades_template.json)")


def write_contact_sheet(out_dir: Path, rows: list[dict], meta: dict) -> None:
    parts = [f"<html><head><meta charset='utf-8'><title>Audit {html.escape(meta['mode'])}</title>",
             "<style>body{font-family:sans-serif;background:#111;color:#eee}"
             "table{border-collapse:collapse;width:100%}td{border:1px solid #333;padding:8px;vertical-align:top}"
             "img{max-width:420px}.flag{color:#ff6b6b;font-weight:bold}</style></head><body>",
             f"<h2>Audit — {html.escape(meta['mode'])} — {meta['sentences']} sentences / {meta['rows']} rows</h2><table>"]
    for r in rows:
        img = (f"<img src='file://{html.escape(r['frame_path'])}'>" if r.get("frame_path")
               else html.escape(str(r.get("graphic_text") or "(no frame)")))
        flags = f"<div class='flag'>{' '.join(r['flags'])}</div>" if r.get("flags") else ""
        parts.append(f"<tr><td><b>{r['row_id']}</b><br>{r['t_start']:.1f}s–{r['t_end']:.1f}s<br>"
                     f"{html.escape(r.get('section_label') or '')}</td><td>{html.escape(r['text'])}{flags}</td>"
                     f"<td>{img}</td></tr>")
    parts.append("</table></body></html>")
    (out_dir / "contact_sheet.html").write_text("".join(parts), encoding="utf-8")


# ---------------------------------------------------------------- lock

def lock(args: argparse.Namespace) -> None:
    """Print the narration hash of a source script, and compare it with a project's script artifact."""
    source_hash = None
    if args.source:
        text = Path(args.source).read_text(encoding="utf-8")
        source_hash = narration_sha256([{"text": text}])
        words = len(tokens(narration_lines(text)))
        print(json.dumps({"source": args.source, "narration_sha256": source_hash, "word_count": words}))
    if args.project:
        script = require(load_artifact(Path(args.project).resolve(), "script", "script"), "script")
        artifact_hash = narration_sha256(script["sections"])
        locked = ((script.get("metadata") or {}).get("script_lock") or {}).get("narration_sha256")
        print(json.dumps({"artifact_narration_sha256": artifact_hash, "locked_sha256": locked}))
        if source_hash and artifact_hash != source_hash:
            sys.exit("[audit] CRITICAL: script artifact narration differs from the source script")
        if locked and locked != artifact_hash:
            sys.exit("[audit] CRITICAL: script artifact narration differs from its locked hash")
    print("[audit] lock check OK")


# ---------------------------------------------------------------- verify

def verify(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    out_dir = project / "audit" / args.mode
    sheet_path, grades_path = out_dir / "audit_sheet.json", out_dir / "grades.json"
    if not sheet_path.exists():
        sys.exit(f"[audit] run `build --mode {args.mode}` first")
    if not grades_path.exists():
        sys.exit(f"[audit] missing {grades_path}; grade every row first")
    sheet = json.loads(sheet_path.read_text(encoding="utf-8"))
    grades = {g["row_id"]: g for g in json.loads(grades_path.read_text(encoding="utf-8"))}

    failures, ungraded = [], []
    for row in sheet["rows"]:
        grade = grades.get(row["row_id"])
        if row.get("flags"):
            failures.append({"row_id": row["row_id"], "text": row["text"], "reason": "flags: " + ", ".join(row["flags"])})
            continue
        if not grade or grade.get("score") is None:
            ungraded.append(row["row_id"])
            continue
        score = int(grade["score"])
        if score < args.min_score or grade.get("hard_fail") or str(grade.get("verdict", "")).upper() != "PASS":
            failures.append({"row_id": row["row_id"], "text": row["text"], "score": score,
                             "hard_fail": grade.get("hard_fail", []), "reason": grade.get("reason", ""),
                             "fix": grade.get("fix", "")})

    lock_ok = sheet["meta"].get("script_lock_ok")
    critical = []
    if lock_ok is False:
        critical.append("Narration text changed after script lock (hash mismatch)")
    status = "PASS" if not failures and not ungraded and not critical and sheet["rows"] else "FAIL"
    scores = [int(g["score"]) for g in grades.values() if g.get("score") is not None]
    report = {"mode": args.mode, "status": status, "min_score": args.min_score,
              "rows": len(sheet["rows"]), "graded": len(scores),
              "average_score": round(sum(scores) / len(scores), 2) if scores else None,
              "ungraded": ungraded, "failures": failures, "critical": critical}
    (out_dir / "audit_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[audit] {args.mode}: {status} — {len(failures)} failures, {len(ungraded)} ungraded, "
          f"avg {report['average_score']}")
    sys.exit(0 if status == "PASS" else 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--project", required=True)
    b.add_argument("--mode", choices=["storyboard", "render"], required=True)
    b.add_argument("--video")
    b.add_argument("--words")
    v = sub.add_parser("verify")
    v.add_argument("--project", required=True)
    v.add_argument("--mode", choices=["storyboard", "render"], required=True)
    v.add_argument("--min-score", type=int, default=4)
    k = sub.add_parser("lock")
    k.add_argument("--source", help="the user's script file (markers allowed)")
    k.add_argument("--project", help="project dir whose script artifact must match")
    args = parser.parse_args()
    {"build": build, "verify": verify, "lock": lock}[args.command](args)


if __name__ == "__main__":
    main()
