#!/usr/bin/env bash
# Runs ON the rented GPU pod (RunPod template "RunPod PyTorch", volume at /workspace).
# First run: installs ComfyUI + downloads the models to the persistent volume (~31 GB images,
# +~45 GB with --video). Next runs: just starts ComfyUI (models are already on the volume).
# ComfyUI listens on 127.0.0.1 only; the Editor server reaches it through an SSH tunnel.
#   bash arrancar-pod.sh            # images (Qwen-Image + Lightning, Apache-2.0)
#   bash arrancar-pod.sh --video    # + Wan 2.2 14B i2v/t2v 4-step (Apache-2.0)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WS="${WORKSPACE:-/workspace}"
CUI="$WS/ComfyUI"
APAGAR_TRAS_MIN="${APAGAR_TRAS_MIN:-20}"   # auto-stop the pod after N idle minutes

if [[ ! -d "$CUI" ]]; then
  git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git "$CUI"
fi
cd "$CUI"
git pull --ff-only || true
python3 -m venv "$WS/venv-comfy" 2>/dev/null || true
. "$WS/venv-comfy/bin/activate"
pip install -q --upgrade pip
pip install -q -r requirements.txt huggingface_hub

get() {  # get <repo> <file in repo> <models subfolder>
  local dest="$CUI/models/$3/$(basename "$2")"
  if [[ -s "$dest" ]]; then echo "  ok  $3/$(basename "$2")"; return; fi
  echo "  ↓   $3/$(basename "$2")"
  python3 - "$1" "$2" "$CUI/models/$3" <<'PY'
import os, shutil, sys
from huggingface_hub import hf_hub_download
repo, path, folder = sys.argv[1:]
tmp = os.path.join(folder, ".descarga")
p = hf_hub_download(repo_id=repo, filename=path, local_dir=tmp)
shutil.move(p, os.path.join(folder, os.path.basename(path)))
shutil.rmtree(tmp, ignore_errors=True)
PY
}
export HF_HOME="$WS/hf-cache"

echo "==> Modelos de imagen (Apache-2.0)"
get Comfy-Org/Qwen-Image split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors diffusion_models
get Comfy-Org/Qwen-Image split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors text_encoders
get Comfy-Org/Qwen-Image split_files/vae/qwen_image_vae.safetensors vae
get lightx2v/Qwen-Image-Lightning Qwen-Image-Lightning-8steps-V2.0.safetensors loras

if [[ "${1:-}" == "--video" ]]; then
  echo "==> Modelos de video Wan 2.2 (Apache-2.0) — los mismos que usan los workflows de OpenMontage"
  W=Comfy-Org/Wan_2.2_ComfyUI_Repackaged
  get $W split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors text_encoders
  get Comfy-Org/Wan_2.1_ComfyUI_repackaged split_files/vae/wan_2.1_vae.safetensors vae
  for f in wan2.2_i2v_high_noise_14B_fp8_scaled wan2.2_i2v_low_noise_14B_fp8_scaled; do
    get $W split_files/diffusion_models/$f.safetensors diffusion_models; done
  for f in wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise; do
    get $W split_files/loras/$f.safetensors loras; done
fi

echo "==> Arrancando ComfyUI en 127.0.0.1:8188 (solo accesible por túnel SSH)"
pkill -f "ComfyUI/main.py" 2>/dev/null || true
nohup python3 "$CUI/main.py" --listen 127.0.0.1 --port 8188 > "$WS/comfyui.log" 2>&1 &
for i in $(seq 1 60); do curl -fs http://127.0.0.1:8188/system_stats >/dev/null && break; sleep 2; done
curl -fs http://127.0.0.1:8188/system_stats >/dev/null && echo "ComfyUI OK" || { echo "ComfyUI no arrancó: ver $WS/comfyui.log"; exit 1; }

pkill -f vigilante.py 2>/dev/null || true
nohup python3 "$HERE/vigilante.py" --minutos "$APAGAR_TRAS_MIN" > "$WS/vigilante.log" 2>&1 &
echo "Vigilante activo: apaga el pod tras $APAGAR_TRAS_MIN min sin trabajo (log: $WS/vigilante.log)"
