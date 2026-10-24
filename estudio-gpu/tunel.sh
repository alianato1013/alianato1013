#!/usr/bin/env bash
# Runs on the Editor server (no GPU). Connects to the rented GPU pod, makes sure ComfyUI is
# installed and running there, opens an SSH tunnel and points OpenMontage at it.
#   bash tunel.sh <IP_DEL_POD> <PUERTO_SSH>   (both from RunPod → your pod → Connect → "SSH over exposed TCP")
#   bash tunel.sh --cerrar                    (close the tunnel; the pod stops itself after 20 idle min)
set -euo pipefail
OM="${OPENMONTAGE_DIR:-$HOME/OpenMontage}"
REPO_URL="https://github.com/alianato1013/alianato1013.git"
REPO_BRANCH="claude/rea-repository-analysis-9eytp3"
if [[ "${1:-}" == "--cerrar" ]]; then
  pkill -f "ssh .*-L 8188:127.0.0.1:8188" && echo "Túnel cerrado." || echo "No había túnel."
  exit 0
fi
IP="${1:?uso: tunel.sh <IP> <PUERTO>}"; PORT="${2:?uso: tunel.sh <IP> <PUERTO>}"
SSH=(ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -p "$PORT" "root@$IP")

echo "==> Preparando el pod (la primera vez descarga ~31 GB de modelos: 10-20 min)"
"${SSH[@]}" "set -e; cd /workspace; \
  if [ -d alianato1013 ]; then git -C alianato1013 pull -q --ff-only || true; \
  else git clone -q --branch $REPO_BRANCH $REPO_URL alianato1013; fi; \
  bash alianato1013/estudio-gpu/arrancar-pod.sh ${GPU_VIDEO:+--video}"

echo "==> Abriendo túnel"
pkill -f "ssh .*-L 8188:127.0.0.1:8188" 2>/dev/null || true
ssh -f -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new \
    -L 8188:127.0.0.1:8188 -p "$PORT" "root@$IP"
sleep 2
curl -fs http://127.0.0.1:8188/system_stats >/dev/null \
  && echo "Túnel OK: la GPU del pod está disponible en http://127.0.0.1:8188" \
  || { echo "El túnel abrió pero ComfyUI no responde"; exit 1; }
if [[ -f "$OM/.env" ]] && ! grep -q '^COMFYUI_SERVER_URL=' "$OM/.env"; then
  echo "COMFYUI_SERVER_URL=http://127.0.0.1:8188" >> "$OM/.env"
  echo "OpenMontage apuntado a la GPU (COMFYUI_SERVER_URL en $OM/.env)"
fi
cd "$OM" && [[ -f .venv/bin/activate ]] && . .venv/bin/activate
python scripts/channel_assets/gen_image.py --check
