#!/usr/bin/env bash
# Brain Storming: one daily cycle for the active niche.
#   data (Espía + competitors + markets + Meta metrics + rules)
#   -> Bibliotecario updates the brain -> Estratega writes report + proposals
#   -> verify -> git commit -> Google Drive backup.
# Nothing is published here: publishing only happens when the owner says "publica <ID>".
# Cron (06:20 Puerto Rico = 10:20 UTC):  20 10 * * * $HOME/alianato1013/brain-storming/run-diario.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="${BRAIN_DATA:-$HOME/brain-data}"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
B="python3 $HERE/brain.py"
FECHA="$(date +%F)"
mkdir -p "$DATA/logs"
exec > >(tee -a "$DATA/logs/$FECHA.log") 2>&1

SLUG="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("nicho_activo",""))' "$DATA/config.json")"
[[ -n "$SLUG" ]] || { echo "No active niche (say 'busca nichos' first)"; exit 1; }
NICHO="$DATA/cerebro/$SLUG"
DIA="$NICHO/diario/$FECHA"

echo "== $(date) data"
$B diario || { echo "diario failed"; exit 1; }

# Model per role + optional API-key billing (see ahorro-tokens/); plain `claude -p` otherwise.
AUTO="$HERE/../ahorro-tokens/claude-auto.sh"
claude_run() {  # $1 = rutina|critico, $2 = prompt, rest = claude args
  local tipo="$1" prompt="$2"; shift 2
  if [[ -x "$AUTO" ]]; then "$AUTO" "$tipo" "$prompt" "$@"; else claude -p "$prompt" "$@"; fi
}
run_role() {  # $1 = role file, $2 = extra message, $3 = log name, $4 = rutina|critico
  ( cd "$DATA" && claude_run "$4" "Sigue al pie de la letra $HERE/roles/$1. Nicho: $NICHO. Carpeta del día: $DIA. Fecha: $FECHA. $2" \
      --allowedTools "Read" "Write" "Edit" "Glob" "Grep" \
      --add-dir "$HERE" --permission-mode acceptEdits ) > "$DIA/$3.txt" 2>&1
}

MODO=""
[[ "$(date +%u)" == "7" ]] && MODO="MODO SEMANAL."
echo "== $(date) bibliotecario $MODO"
run_role BIBLIOTECARIO.md "$MODO" bibliotecario rutina

MSG="Escribe $DIA/REPORTE.md y las propuestas de hoy en $NICHO/propuestas/."
for attempt in 1 2; do
  echo "== $(date) estratega (attempt $attempt)"
  run_role ESTRATEGA.md "$MSG" "estratega-$attempt" critico
  if CHECK="$($B verificar 2>&1)"; then echo "$CHECK"; rm -f "$DIA/NO-VERIFICADO.txt"; break; fi
  echo "$CHECK"
  MSG="El verificador rechazó el trabajo de hoy por esto: $CHECK. Corrige $DIA/REPORTE.md y/o las propuestas de hoy en $NICHO/propuestas/ (no toques las de días anteriores)."
  [[ $attempt == 2 ]] && echo "$CHECK" > "$DIA/NO-VERIFICADO.txt"
done

git -C "$DATA" add -A && git -C "$DATA" commit -q -m "ciclo $SLUG $FECHA" || true

DRIVE="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("drive_folder",""))' "$DATA/config.json")"
if [[ -n "$DRIVE" ]] && command -v rclone >/dev/null; then
  echo "== $(date) backup to $DRIVE"
  rclone copy "$DATA" "$DRIVE" --exclude ".git/**" --exclude "**/raw/**" --exclude "**/raw-seguimiento/**" \
    && echo "Backup OK: $DRIVE/cerebro/$SLUG/diario/$FECHA/REPORTE.md"
fi

# Raw API responses are evidence for 30 days; the brain and reports are kept forever.
find "$NICHO/diario" -mindepth 2 -maxdepth 2 \( -name raw -o -name raw-seguimiento -o -name landings \) \
  -type d -mtime +30 -exec rm -rf {} + 2>/dev/null
command -v ccusage >/dev/null && ccusage claude daily --since "$FECHA" > "$DATA/logs/uso-$FECHA.txt" 2>&1
echo "== $(date) done"
