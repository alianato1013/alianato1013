#!/usr/bin/env bash
# Editor Supremo installer — copies the channel overlay into an OpenMontage checkout.
# Usage: bash install.sh /path/to/OpenMontage
set -euo pipefail

TARGET="${1:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "$TARGET" || ! -f "$TARGET/AGENT_GUIDE.md" || ! -d "$TARGET/pipeline_defs" ]]; then
  echo "Usage: bash install.sh /path/to/OpenMontage   (the folder that contains AGENT_GUIDE.md)" >&2
  exit 1
fi

cp -R "$HERE/overlay/." "$TARGET/"

BEGIN="<!-- EDITOR-SUPREMO:BEGIN -->"
END="<!-- EDITOR-SUPREMO:END -->"
BLOCK="$BEGIN
## CHANNEL MODE (Editor Supremo — local overlay, highest priority)
If the request involves **Hard Times Heritage**, **Sumerian Vault** or **Beneath America**
(or the codes HTH / SV / BA, or a project id starting with hth- / sv- / ba-), read
[\`CHANNELS.md\`](CHANNELS.md) FIRST and follow it before any other routing in this repo.
$END"

patch() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  python3 - "$file" "$BEGIN" "$END" "$BLOCK" <<'PY'
import re, sys
path, begin, end, block = sys.argv[1:5]
text = open(path, encoding="utf-8").read()
text = re.sub(re.escape(begin) + r".*?" + re.escape(end) + r"\n*", "", text, flags=re.S)
lines = text.split("\n", 1)
if lines[0].startswith("# "):
    text = lines[0] + "\n\n" + block + "\n\n" + (lines[1].lstrip("\n") if len(lines) > 1 else "")
else:
    text = block + "\n\n" + text
open(path, "w", encoding="utf-8").write(text)
PY
  echo "patched $file"
}

for f in CLAUDE.md AGENTS.md AGENT_GUIDE.md CODEX.md CURSOR.md COPILOT.md; do
  patch "$TARGET/$f"
done

echo
echo "Validating..."
( cd "$TARGET" && python3 - <<'PY'
import sys
sys.path.insert(0, ".")
from styles.playbook_loader import load_playbook
from lib.pipeline_loader import load_pipeline
for name in ("hard-times-heritage", "sumerian-vault", "beneath-america"):
    load_playbook(name)
    print("  OK playbook", name)
load_pipeline("channel-documentary")
print("  OK pipeline channel-documentary")
PY
)
echo "Editor Supremo installed in $TARGET"
