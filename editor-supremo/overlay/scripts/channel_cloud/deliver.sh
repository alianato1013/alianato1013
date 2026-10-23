#!/usr/bin/env bash
# Editor Supremo — deliver a finished video to cloud storage and free the server disk.
#
# Usage (from the OpenMontage folder):
#   bash scripts/channel_cloud/deliver.sh <project-id> [--keep]
#
# Requirements:
#   - render audit passed: projects/<id>/audit/render/audit_report.json  status = PASS
#   - rclone remote configured (default "gdrive:"; override with OM_REMOTE="name:Folder")
#
# What it does:
#   1. Uploads final.mp4, thumbnails, publish package, audit reports and the source script to
#      <remote>/YouTube/<Channel>/<project-id>/
#   2. Verifies the upload (size + checksum when available)
#   3. Deletes the heavy files on the server (assets, renders, frames) unless --keep is given.
#      Small JSON artifacts, checkpoints and the script stay, so the project history is kept.
set -euo pipefail

PROJECT_ID="${1:-}"
KEEP="${2:-}"
if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: bash scripts/channel_cloud/deliver.sh <project-id> [--keep]" >&2
  exit 1
fi

OM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
P="$OM_DIR/projects/$PROJECT_ID"
REMOTE_ROOT="${OM_REMOTE:-gdrive:YouTube}"

case "$PROJECT_ID" in
  hth-*) CHANNEL="Hard Times Heritage" ;;
  sv-*)  CHANNEL="Sumerian Vault" ;;
  ba-*)  CHANNEL="Beneath America" ;;
  *) echo "Project id must start with hth-, sv- or ba-" >&2; exit 1 ;;
esac

[[ -d "$P" ]] || { echo "Project not found: $P" >&2; exit 1; }
FINAL="$P/renders/final.mp4"
[[ -f "$FINAL" ]] || { echo "Missing $FINAL — render first." >&2; exit 1; }

REPORT="$P/audit/render/audit_report.json"
STATUS="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('status',''))" "$REPORT" 2>/dev/null || true)"
if [[ "$STATUS" != "PASS" ]]; then
  echo "BLOCKED: render audit is not PASS ($REPORT). Nothing was uploaded." >&2
  exit 1
fi

REMOTE_NAME="${REMOTE_ROOT%%:*}"
if ! rclone listremotes | grep -qx "${REMOTE_NAME}:"; then
  echo "rclone remote '${REMOTE_NAME}:' is not configured. Run: rclone config" >&2
  exit 1
fi

DEST="$REMOTE_ROOT/$CHANNEL/$PROJECT_ID"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

cp "$FINAL" "$STAGE/"
find "$P/renders" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.srt' -o -iname '*.vtt' \) -exec cp {} "$STAGE/" \;
[[ -f "$P/inputs/script_source.md" ]] && cp "$P/inputs/script_source.md" "$STAGE/"
for mode in storyboard render; do
  [[ -f "$P/audit/$mode/audit_report.json" ]] && cp "$P/audit/$mode/audit_report.json" "$STAGE/audit_${mode}.json"
done
[[ -f "$P/checkpoint_publish.json" ]] && cp "$P/checkpoint_publish.json" "$STAGE/publish_package.json"
for d in "$P/exports" "$P/export" "$P/publish"; do
  [[ -d "$d" ]] && cp -R "$d" "$STAGE/publish_bundle"
done

echo "==> Uploading to $DEST"
rclone copy "$STAGE" "$DEST" --progress --transfers 4

echo "==> Verifying"
rclone check "$STAGE" "$DEST" --one-way

LINK="$(rclone link "$DEST/final.mp4" 2>/dev/null || true)"
{
  echo "delivered_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "remote=$DEST"
  [[ -n "$LINK" ]] && echo "link=$LINK"
} > "$P/DELIVERED.txt"

if [[ "$KEEP" != "--keep" ]]; then
  echo "==> Freeing server disk (keeping JSON artifacts, checkpoints and the script)"
  rm -rf "$P/assets" "$P/renders" "$P/audit/storyboard/frames" "$P/audit/render/frames"
  find "$P/audit" -type f \( -iname '*.mp4' -o -iname '*.wav' -o -iname '*.mp3' \) -delete 2>/dev/null || true
fi

echo
echo "DELIVERED: $DEST"
[[ -n "$LINK" ]] && echo "Link: $LINK"
df -h "$OM_DIR" | tail -1 | awk '{print "Server disk used: "$5" ("$4" free)"}'
