#!/usr/bin/env bash
# Editor Supremo — prepares a fresh Ubuntu 24.04 cloud server for OpenMontage + Claude Code.
# Run ONCE as root:   bash setup-server.sh [username]
# Default username: editor
set -euo pipefail

USERNAME="${1:-editor}"
REPO_URL="https://github.com/alianato1013/alianato1013.git"
REPO_BRANCH="claude/rea-repository-analysis-9eytp3"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root (ssh root@<server-ip>, then: bash setup-server.sh)" >&2
  exit 1
fi

echo "==> System packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y upgrade
apt-get install -y git curl unzip tmux htop ufw ca-certificates \
  python3 python3-venv python3-pip ffmpeg fontconfig fonts-liberation fonts-dejavu \
  libnss3 libatk-bridge2.0-0t64 libatk1.0-0t64 libcups2t64 libdrm2 libgbm1 libgtk-3-0t64 \
  libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 libasound2t64 libpango-1.0-0 libcairo2

echo "==> Node.js 20"
if ! command -v node >/dev/null || [[ "$(node -v | cut -c2- | cut -d. -f1)" -lt 18 ]]; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
fi

echo "==> rclone (cloud storage sync)"
command -v rclone >/dev/null || curl -fsSL https://rclone.org/install.sh | bash

echo "==> Channel fonts (Playfair Display, Lora, Cormorant Garamond, Montserrat, Inter)"
FONT_DIR=/usr/local/share/fonts/editor-supremo
mkdir -p "$FONT_DIR"
for f in "playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf" "playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf" \
         "lora/Lora%5Bwght%5D.ttf" "lora/Lora-Italic%5Bwght%5D.ttf" \
         "cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf" "cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf" \
         "montserrat/Montserrat%5Bwght%5D.ttf" "inter/Inter%5Bopsz,wght%5D.ttf"; do
  name="$(basename "$f" | sed 's/%5B/[/; s/%5D/]/')"
  curl -fsSL -o "$FONT_DIR/$name" "https://raw.githubusercontent.com/google/fonts/main/ofl/$f" \
    || echo "   warning: could not download $name"
done
fc-cache -f >/dev/null

echo "==> Swap (8 GB) so long renders never run out of memory"
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 8G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "==> Firewall: SSH only"
ufw allow OpenSSH
ufw --force enable

echo "==> User $USERNAME"
if ! id "$USERNAME" >/dev/null 2>&1; then
  adduser --disabled-password --gecos "" "$USERNAME"
  usermod -aG sudo "$USERNAME"
  echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/90-$USERNAME"
fi
mkdir -p "/home/$USERNAME/.ssh"
[[ -f /root/.ssh/authorized_keys ]] && cp /root/.ssh/authorized_keys "/home/$USERNAME/.ssh/"
chown -R "$USERNAME:$USERNAME" "/home/$USERNAME/.ssh"
chmod 700 "/home/$USERNAME/.ssh"

echo "==> OpenMontage + Editor Supremo + Claude Code (as $USERNAME)"
sudo -iu "$USERNAME" REPO_URL="$REPO_URL" REPO_BRANCH="$REPO_BRANCH" bash <<'EOF'
set -euo pipefail
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
grep -q 'npm-global/bin' ~/.bashrc || echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.npm-global/bin:$PATH"
npm install -g @anthropic-ai/claude-code

[[ -d ~/OpenMontage ]] || git clone https://github.com/calesthio/OpenMontage.git ~/OpenMontage
cd ~/OpenMontage
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install piper-tts
python -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
( cd remotion-composer && npm install && (npx --yes remotion browser ensure || true) )
[[ -f .env ]] || cp .env.example .env
grep -q 'activate' ~/.bashrc || echo 'cd ~/OpenMontage && . .venv/bin/activate' >> ~/.bashrc

if [[ -d ~/alianato1013 ]]; then
  git -C ~/alianato1013 pull --ff-only
else
  git clone --branch "$REPO_BRANCH" "$REPO_URL" ~/alianato1013
fi
bash ~/alianato1013/editor-supremo/install.sh ~/OpenMontage
mkdir -p ~/guiones ~/.config/editor-supremo/youtube
chmod 700 ~/.config/editor-supremo ~/.config/editor-supremo/youtube
EOF

echo
echo "DONE. Next steps (see PASO-A-PASO-NUBE.md):"
echo "  1. ssh $USERNAME@<server-ip>"
echo "  2. nano ~/OpenMontage/.env        (paste your API keys)"
echo "  3. rclone config                  (connect Google Drive as 'gdrive')"
echo "  4. tmux new -s editor ; claude    (log in once), then: claude remote-control"
