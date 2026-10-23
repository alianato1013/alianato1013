#!/usr/bin/env bash
# claude-auto.sh <rutina|critico> "<prompt>" [extra claude args...]
# Runs Claude Code headless for automated jobs with the right model and, when an
# Anthropic API key is configured, on pay-per-use billing with a hard per-run cap,
# so scheduled jobs never wait on (or eat) the subscription's 5-hour/weekly limits.
set -uo pipefail
CONF_DIR="$HOME/.config/ahorro-tokens"
MODELO_RUTINA="sonnet"; MODELO_CRITICO="opus"; MODELO_RESPALDO="sonnet"
USAR_API_EN_CRON=1; TOPE_USD_POR_CORRIDA="1.50"
[[ -f "$CONF_DIR/config.sh" ]] && . "$CONF_DIR/config.sh"

TIPO="${1:?usage: claude-auto.sh <rutina|critico> \"prompt\" [args]}"; shift
PROMPT="${1:?missing prompt}"; shift
case "$TIPO" in
  rutina)  MODELO="$MODELO_RUTINA" ;;
  critico) MODELO="$MODELO_CRITICO" ;;
  *) echo "tipo must be rutina or critico" >&2; exit 2 ;;
esac
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

EXTRA=()
if [[ "$USAR_API_EN_CRON" == "1" && -s "$CONF_DIR/anthropic_api_key" ]]; then
  ANTHROPIC_API_KEY="$(tr -d '[:space:]' < "$CONF_DIR/anthropic_api_key")"
  export ANTHROPIC_API_KEY
  EXTRA+=(--max-budget-usd "$TOPE_USD_POR_CORRIDA")
  echo "[claude-auto] $TIPO · model=$MODELO · billing=API key · cap=US\$$TOPE_USD_POR_CORRIDA" >&2
else
  unset ANTHROPIC_API_KEY
  echo "[claude-auto] $TIPO · model=$MODELO · billing=subscription" >&2
fi
[[ "$MODELO" != "$MODELO_RESPALDO" ]] && EXTRA+=(--fallback-model "$MODELO_RESPALDO")

exec claude -p "$PROMPT" --model "$MODELO" "${EXTRA[@]}" "$@"
