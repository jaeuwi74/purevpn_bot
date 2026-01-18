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

# Demander l'email
read -p "Entrez votre email PureVPN : " pure_email
# Demander le mot de passe (saisie masquée pour plus de sécurité)
read -s -p "Entrez votre mot de passe PureVPN : " pure_pass
echo "" # Pour revenir à la ligne après la saisie masquée

# Création du fichier .env
cat <<EOF > .env
EMAIL=$pure_email
PASSWORD=$pure_pass
EOF
chmod 600 .env 


# 2. Création du fichier Service pour le Bot
echo -e "${GREEN}⚙️ Configuration du service systemd : purevpn-bot.service${NC}"
sudo bash -c "cat <<EOF > /etc/systemd/system/purevpn-bot.service
[Unit]
Description=PureVPN Bot
After=network.target

[Service]
Type=oneshot
User=$USER
ExecStartPre=/bin/sleep 60
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/purevpn_bot.py
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
sudo systemctl enable purevpn-bot.service

sudo systemctl daemon-reload

# 5. On lance le bot UNE PREMIÈRE FOIS manuellement pour créer le fichier wg0.conf
echo -e "${GREEN}🔄 Génération de la première configuration VPN...${NC}"
./venv/bin/python3 purevpn_bot.py

# 6 Maintenant que le fichier existe, on peut démarrer le VPN en toute sécurité
echo -e "${GREEN}🔌 Démarrage de WireGuard...${NC}"
sudo systemctl enable --now wg-quick@wg0.service
echo -e "${GREEN}✅ Configuration système terminée.${NC}"

