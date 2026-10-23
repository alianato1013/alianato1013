#!/usr/bin/env bash
# Ahorro de tokens para Claude Code en el servidor (usuario editor). Idempotente.
#  1. rtk (edición OSS, Apache-2.0): comprime la salida de la terminal antes de que llegue a Claude
#  2. ccusage: mide el consumo por día, sesión y ventana de 5 horas
#  3. Playwright MCP: navegador que lee páginas como texto (más barato que capturas)
#  4. claude-auto.sh: modelo por tarea + llave de API opcional para las tareas automáticas
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
HERE="$(cd "$(dirname "$0")" && pwd)"
CONF_DIR="$HOME/.config/ahorro-tokens"
command -v claude >/dev/null || { echo "Claude Code no está instalado (ver PASO-A-PASO-NUBE.md)"; exit 1; }
command -v npm >/dev/null || { echo "Falta Node/npm (ver setup-server.sh)"; exit 1; }

echo "==> 1/4 rtk (edición OSS)"
if ! command -v rtk >/dev/null; then
  TMP="$(mktemp -d)"
  curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh -o "$TMP/install.sh"
  echo "    instalador descargado de github.com/rtk-ai/rtk (sha256: $(sha256sum "$TMP/install.sh" | cut -c1-16)…)"
  RTK_EDITION=oss sh "$TMP/install.sh"
  rm -rf "$TMP"
  hash -r
fi
rtk gain >/dev/null 2>&1 && echo "    rtk OK" || { echo "    rtk no responde: revisa la instalación"; exit 1; }
echo "    Conectando rtk a Claude Code (hook global). Si te pregunta por el 'proxy', responde NO."
rtk init -g

echo "==> 2/4 ccusage"
command -v ccusage >/dev/null || npm install -g ccusage
ccusage --version >/dev/null 2>&1 && echo "    ccusage OK"

echo "==> 3/4 Playwright MCP (navegador sin pantalla)"
if ! claude mcp list 2>/dev/null | grep -q '^playwright'; then
  claude mcp add -s user playwright -- npx -y @playwright/mcp@latest --headless --isolated
fi
npx -y playwright@latest install chromium >/dev/null 2>&1 \
  && echo "    Chromium OK" \
  || echo "    AVISO: si Playwright falla, ejecuta una vez como root: npx -y playwright@latest install-deps chromium"

echo "==> 4/4 claude-auto.sh (modelo por tarea + llave de API opcional)"
mkdir -p "$CONF_DIR" && chmod 700 "$CONF_DIR"
[[ -f "$CONF_DIR/config.sh" ]] || cp "$HERE/config.ejemplo.sh" "$CONF_DIR/config.sh"
chmod +x "$HERE/claude-auto.sh"
if [[ ! -s "$CONF_DIR/anthropic_api_key" ]]; then
  read -r -s -p "    Pega tu llave de API de Anthropic (Enter para omitir y usar tu suscripción): " KEY; echo
  if [[ -n "${KEY:-}" ]]; then
    umask 077; printf '%s\n' "$KEY" > "$CONF_DIR/anthropic_api_key"; unset KEY
    echo "    Llave guardada en $CONF_DIR/anthropic_api_key (solo tú puedes leerla)"
  fi
fi
echo
echo "LISTO. Comprueba con:  bash $HERE/uso.sh"
