#!/usr/bin/env bash
# Espía de ofertas: one daily run. collect evidence -> Claude writes the report ->
# verify the report against the evidence -> upload to Google Drive.
# Cron example (06:40 every day):  40 6 * * * $HOME/alianato1013/espia-ofertas/run-daily.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
DATE="$(date +%F)"
RUN="$HERE/runs/$DATE"
CONFIG="$HERE/config.json"
LOG="$HERE/runs/$DATE.log"
mkdir -p "$HERE/runs"
exec > >(tee -a "$LOG") 2>&1

[[ -f "$CONFIG" ]] || { echo "Missing $CONFIG (copy config.example.json)"; exit 1; }
DRIVE="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("drive_folder",""))' "$CONFIG")"

echo "== $(date) scan"
python3 "$HERE/espia.py" scan --config "$CONFIG" --out "$RUN" || { echo "scan failed"; exit 1; }

PROMPT="Sigue al pie de la letra las instrucciones de $HERE/ANALISTA.md. La carpeta del día es $RUN. Lee $RUN/dossier.json y $RUN/EVIDENCIA.md y escribe $RUN/REPORTE.md."
for attempt in 1 2; do
  echo "== $(date) analyst (attempt $attempt)"
  AUTO="$HERE/../ahorro-tokens/claude-auto.sh"   # model + API-key billing when installed
  CLAUDE_CMD=(claude -p "$PROMPT"); [[ -x "$AUTO" ]] && CLAUDE_CMD=("$AUTO" critico "$PROMPT")
  ( cd "$RUN" && "${CLAUDE_CMD[@]}" \
      --allowedTools "Read" "Write" "Edit" "Glob" "Grep" \
      --add-dir "$HERE" --permission-mode acceptEdits ) > "$RUN/analyst-$attempt.txt" 2>&1
  if [[ -f "$RUN/REPORTE.md" ]] && CHECK="$(python3 "$HERE/espia.py" check-report --run "$RUN")"; then
    echo "$CHECK"
    break
  fi
  CHECK="$(python3 "$HERE/espia.py" check-report --run "$RUN" 2>&1 || true)"
  echo "$CHECK"
  PROMPT="El verificador rechazó $RUN/REPORTE.md por esto: $CHECK. Corrígelo siguiendo $HERE/ANALISTA.md, usando solo datos de $RUN/dossier.json."
  if [[ $attempt == 2 ]]; then
    echo "REPORT NOT VERIFIED" > "$RUN/NO-VERIFICADO.txt"
  fi
done

if [[ -n "$DRIVE" ]] && command -v rclone >/dev/null; then
  echo "== $(date) upload to $DRIVE/$DATE"
  rclone copy "$RUN" "$DRIVE/$DATE" --exclude "raw/**" --exclude "analyst-*.txt" \
    && rclone copy "$RUN/raw" "$DRIVE/$DATE/raw" \
    && rclone check "$RUN" "$DRIVE/$DATE" --one-way --exclude "analyst-*.txt" \
    && echo "Uploaded: $DRIVE/$DATE"
fi

# Keep 30 days of runs on the server (they are small: JSON + HTML, no videos).
find "$HERE/runs" -mindepth 1 -maxdepth 1 -mtime +30 -exec rm -rf {} +
echo "== $(date) done"
