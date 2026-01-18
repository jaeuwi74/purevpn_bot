#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m'
PROJECT_DIR=$(pwd)

echo -e "${GREEN}🚀 Début de l'installation complète...${NC}"

# 1. Installation Python et Environnement
sudo apt update && sudo apt install -y python3-venv python3-pip wireguard
python3 -m venv venv
./venv/bin/pip install playwright python-dotenv
./venv/bin/playwright install chromium
./venv/bin/playwright install-deps

# 2. Création du fichier Service pour le Bot
echo -e "${GREEN}⚙️ Configuration du service systemd : purevpn-bot.service${NC}"
sudo bash -c "cat <<EOF > /etc/systemd/system/purevpn-bot.service
[Unit]
Description=PureVPN Bot
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/purevpn-bot.py
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF"

# 3. Création de la dépendance pour WireGuard (Override)
echo -e "${GREEN}🔗 Liaison de WireGuard au Bot...${NC}"
WG_OVERRIDE_DIR="/etc/systemd/system/wg-quick@wg0.service.d"
sudo mkdir -p "$WG_OVERRIDE_DIR"
sudo bash -c "cat <<EOF > $WG_OVERRIDE_DIR/override.conf
[Unit]
Requires=purevpn-bot.service
After=purevpn-bot.service
EOF"

# 4. Activation et rechargement
sudo systemctl daemon-reload
echo -e "${GREEN}✅ Configuration système terminée.${NC}"

# 5. Préparation du .env
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || echo -e "PURE_EMAIL=\nPURE_PASS=" > .env
    echo -e "⚠️ N'oublie pas de remplir tes identifiants dans le fichier .env !"
fi