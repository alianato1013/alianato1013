#!/usr/bin/env bash
# Resumen de consumo: lo que ahorró rtk y lo que gastó Claude Code.
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
echo "=== Ahorro de rtk (salida de terminal comprimida) ==="
rtk gain 2>/dev/null || echo "rtk no instalado"
echo; echo "=== Claude Code: últimos 7 días (ccusage) ==="
ccusage claude daily --since "$(date -d '7 days ago' +%F)" --breakdown 2>/dev/null || echo "ccusage no instalado"
echo; echo "=== Ventana de 5 horas actual ==="
ccusage blocks 2>/dev/null | tail -15 || true
