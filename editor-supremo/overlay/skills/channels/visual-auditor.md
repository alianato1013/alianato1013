# Visual Auditor — script ↔ image gate (channel-documentary)

## When to Use

Mandatory, twice per video:
1. **`storyboard_audit`** (sub-stage of `edit`): on the edit timeline, before compose.
2. **`render_audit`** (sub-stage of `compose`): on the rendered `final.mp4`, before delivery.

Purpose: **no image may be on screen unless it represents what the audience is hearing at
that moment.** The audit is a gate, not advice. It is the one exception to the reviewer's
"advisory only" rule.

## Prerequisites

| Requirement | Where |
|---|---|
| Channel bible, sections "Visual rules per line", "Forbidden imagery" and "Audit" | `channels/<channel>/CHANNEL_BIBLE.md` |
| Locked script | `checkpoint_script.json` (`metadata.script_lock`) |
| `edit_decisions` + `asset_manifest` (+ `scene_plan`) | project checkpoints |
| Audit tool | `scripts/channel_audit/audit.py` (build / verify / lock) |
| Image viewing | Your own multimodal image reading (open every frame file) |

## Process

### Step 0 — Lock check
```bash
python scripts/channel_audit/audit.py lock --source projects/<id>/inputs/script_source.md --project projects/<id>
```
If it fails, the narration was altered. Restore the locked text before anything else.

### Step 1 — Build the sheet
Storyboard:
```bash
python scripts/channel_audit/audit.py build --project projects/<id> --mode storyboard
```
Render (word timings first, using the registry `transcriber` tool on the final file; save the
JSON in `projects/<id>/audit/render/`):
```bash
python scripts/channel_audit/audit.py build --project projects/<id> --mode render \
  --video projects/<id>/renders/final.mp4 --words projects/<id>/audit/render/<transcript>.json
```
The tool writes `audit_sheet.json`, `grades_template.json`, `contact_sheet.html` and frames.
One row = one narrated sentence × one visual shown while it is spoken.

Rows flagged `NO_VISUAL`, `GAP_…`, `ASSET_FILE_MISSING` or `FRAME_EXTRACTION_FAILED` are
automatic failures. Fix the timeline or the asset; do not grade around them.

### Step 2 — Grade every row by LOOKING at the pixels
Copy `grades_template.json` to `grades.json`. For each row:
1. Read the sentence (`text`) and the section label.
2. **Open the image file at `frame_path`** with your image-reading ability. For `graphic` rows
   in storyboard mode (text cards, stat cards), read `graphic_text`.
3. Grade with the rubric below and fill: `score` (1–5), `verdict` (`PASS`/`FAIL`),
   `hard_fail` (list of codes, empty if none), `reason` (one line: what the image shows vs what
   the line says) and `fix` (what visual would represent the line).

**Grading from the prompt, the filename or the scene description instead of the actual image
is a CRITICAL violation.** Prompts lie; pixels don't.

Work in batches of 10–15 rows. For a 25-minute video expect 300–500 rows: grade them all.

### Rubric

| Score | Meaning | Verdict |
|---|---|---|
| **5** | Shows exactly the subject, action, place and era of the line | PASS |
| **4** | Clearly represents the line's subject; minor generic details | PASS (if ≥ the bible's minimum) |
| **3** | Same general topic but not what this line says (generic filler B-roll) | FAIL |
| **2** | Loosely related | FAIL |
| **1** | Unrelated, contradictory or misleading | FAIL |

"Represents the line" means the **main noun or action of the sentence** is visible: if the
line says "a coffee can behind the flour", a kitchen without a coffee can is a 3. For abstract
lines (emotions, conclusions, transitions), an image that shows the emotion, the subject of
the section, or a bible-approved graphic (title card, stat card, quote card) can be a 4–5.
The bible's "Visual rules per line" section decides channel-specific cases.

### Hard-fail codes (FAIL regardless of score)
- `ANACHRONISM`: an object, clothing, vehicle or technology from the wrong era for the line.
- `WRONG_PLACE`: the line names a place and the image shows another identifiable place.
- `WRONG_COUNT_OR_SUBJECT`: the line says "a widow alone" and the image shows a family, etc.
- `AI_ARTIFACT`: malformed hands or faces, melted objects, garbled pseudo-text, extra limbs.
- `TEXT_OR_WATERMARK`: stock watermarks, foreign UI, unintended readable text.
- `REAL_PERSON_AI`: an AI image presented as a specific real, identifiable person.
- `FORBIDDEN`: anything on the bible's "Forbidden imagery" list.
- `TONE_CLASH`: the image contradicts the emotion of the line (smiling party on a line about grief).
- `OCCLUDED` (render mode only): subtitles or overlays cover the subject that makes the image relevant.
- `STYLE_BREAK`: palette, look or texture clearly outside the channel playbook.

### Step 3 — Verify
```bash
python scripts/channel_audit/audit.py verify --project projects/<id> --mode <storyboard|render> --min-score <bible minimum>
```
Exit code 0 + `audit_report.json` with `status: PASS` is the only acceptable result.

### Step 4 — Fix loop (until PASS)
For every failure, in this order:
1. **Re-pick**: another asset that is already in the manifest and fits the line better.
2. **Re-source**: a new real or licensed image, following the bible's sourcing order. Record the license.
3. **Re-generate**: an AI image whose prompt is built from the line itself plus the playbook
   prefix and negative prompt (bible "AI prompt recipe"). Generate 2 takes and keep the better one.
4. **Re-cut**: split a long cut so each sentence gets its own visual; never stretch one image
   across lines it does not represent.

Then update `asset_manifest` and `edit_decisions`, run `build` again, re-grade the failed rows
**and their neighbours**, and run `verify` again.
After 3 full rounds with failures still open: stop, show the user the failing rows (sentence,
frame, reason, proposed fix) and ask how to proceed. Never deliver with failures.

### Step 5 — Record
- Attach `audit_report.json` (summary) to the stage checkpoint metadata.
- Add a `decision_log` entry: rounds, rows fixed, average score.
- At the gate, show the user the contact sheet path, the average score and the number of fixes.

## Never
- Never lower the minimum score, skip rows, sample instead of grading all, or mark PASS without opening the image.
- Never "fix" a failure by editing the narration.
- Never let compose start before `storyboard_audit` passes, or present `final.mp4` before `render_audit` passes.
