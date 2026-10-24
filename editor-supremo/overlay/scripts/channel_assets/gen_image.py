#!/usr/bin/env python3
"""Generate channel images on our own ComfyUI GPU (Qwen-Image + Lightning LoRA, Apache-2.0).

Runs inside the OpenMontage checkout (the Editor Supremo overlay installs it at
scripts/channel_assets/). Uses OpenMontage's ComfyUI client, so the server is the
same COMFYUI_SERVER_URL (default http://127.0.0.1:8188, reached through tunel.sh).

  # one image, channel style applied, 2 takes (CHANNEL_BIBLE section 6)
  python scripts/channel_assets/gen_image.py --channel hard-times-heritage \
      --prompt "a coffee can full of coins hidden behind flour sacks in a pantry" \
      --out projects/hth-25/assets/images/item24.png --takes 2

  # many images in one GPU session: one JSON object per line {"prompt": ..., "out": ...}
  python scripts/channel_assets/gen_image.py --channel hard-times-heritage --batch prompts.jsonl

Every image gets a sidecar <image>.json with model, license, prompt and seed for asset_manifest.
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools._comfyui.client import ComfyUIClient, ComfyUIError  # noqa: E402

WORKFLOW = Path(__file__).resolve().parent / "workflows" / "qwen-image-lightning.json"
REQUIRED = ["qwen_image_fp8_e4m3fn.safetensors", "qwen_2.5_vl_7b_fp8_scaled.safetensors",
            "qwen_image_vae.safetensors", "Qwen-Image-Lightning-8steps-V2.0.safetensors"]
MODEL = "Qwen-Image fp8 + Qwen-Image-Lightning 8-step V2.0 (self-hosted ComfyUI)"
LICENSE = "AI-generated on own GPU; models Apache-2.0 (Qwen/Qwen-Image, lightx2v/Qwen-Image-Lightning)"


def channel_style(channel):
    """Return (prefix, negative) from styles/custom/<channel>.yaml (asset_generation block)."""
    if not channel:
        return "", ""
    path = ROOT / "styles" / "custom" / f"{channel}.yaml"
    if not path.exists():
        sys.exit(f"Unknown channel style: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
        ag = (yaml.safe_load(text) or {}).get("asset_generation") or {}
        return ag.get("image_prompt_prefix", ""), ag.get("image_negative_prompt", "")
    except ImportError:
        pre = re.search(r'image_prompt_prefix:\s*"([^"]*)"', text)
        neg = re.search(r'image_negative_prompt:\s*"([^"]*)"', text)
        return (pre.group(1) if pre else ""), (neg.group(1) if neg else "")


def generate_one(client, base, prompt, negative, out, width, height, seed):
    out.parent.mkdir(parents=True, exist_ok=True)
    wf = ComfyUIClient.patch_workflow(base, {
        "6": {"text": prompt},
        "7": {"text": negative},
        "8": {"width": width, "height": height, "batch_size": 1},
        "9": {"seed": seed},
        "11": {"filename_prefix": out.stem},
    })
    t0 = time.time()
    paths = client.generate(wf, output_node="11", dest=out, timeout=900)
    final = Path(paths[0])
    if final != out:
        final.replace(out)
    meta = {"source": "ai_generated", "provider": "comfyui-self-hosted", "model": MODEL,
            "license": LICENSE, "prompt": prompt, "negative_prompt": negative, "seed": seed,
            "width": width, "height": height, "server": client.server_url,
            "seconds": round(time.time() - t0, 1), "cost_usd": 0.0,
            "note": "cost is GPU rental time, not per image"}
    out.with_suffix(out.suffix + ".json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return out, meta["seconds"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--channel", help="playbook name in styles/custom/ (adds prefix + negative)")
    ap.add_argument("--prompt")
    ap.add_argument("--out", help="output .png path")
    ap.add_argument("--batch", help="JSONL file: {\"prompt\": ..., \"out\": ...} per line")
    ap.add_argument("--takes", type=int, default=1, help="variants per prompt (_t1, _t2...)")
    ap.add_argument("--width", type=int, default=1664)
    ap.add_argument("--height", type=int, default=928)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--check", action="store_true", help="only check server + models")
    a = ap.parse_args()

    client = ComfyUIClient(capability="image")
    if not client.is_available():
        sys.exit(f"ComfyUI not reachable at {client.server_url}. Start the GPU pod and run tunel.sh.")
    _, missing = client.check_models(REQUIRED)
    if missing:
        sys.exit("ComfyUI is up but models are missing: " + ", ".join(missing) +
                 "\nRun arrancar-pod.sh on the GPU pod.")
    if a.check:
        print(f"OK: {client.server_url} ready with Qwen-Image + Lightning")
        return

    prefix, negative = channel_style(a.channel)
    jobs = []
    if a.batch:
        for line in Path(a.batch).read_text(encoding="utf-8").splitlines():
            if line.strip():
                j = json.loads(line)
                jobs.append((j["prompt"], Path(j["out"]), j.get("width", a.width),
                             j.get("height", a.height)))
    elif a.prompt and a.out:
        jobs.append((a.prompt, Path(a.out), a.width, a.height))
    else:
        sys.exit("Give --prompt and --out, or --batch")

    base = ComfyUIClient.load_workflow(WORKFLOW)
    total, done = time.time(), 0
    for prompt, out, w, h in jobs:
        for t in range(1, a.takes + 1):
            target = out if a.takes == 1 else out.with_name(f"{out.stem}_t{t}{out.suffix}")
            seed = a.seed if (a.seed is not None and a.takes == 1) else ComfyUIClient.random_seed()
            try:
                path, secs = generate_one(client, base, prefix + prompt, negative, target, w, h, seed)
                done += 1
                print(f"[{done}] {path} ({secs}s)")
            except ComfyUIError as e:
                print(f"FAILED {target}: {e}", file=sys.stderr)
    mins = (time.time() - total) / 60
    print(f"Done: {done} images in {mins:.1f} min of GPU time.")


if __name__ == "__main__":
    main()
