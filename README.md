# 🛡️ PureVPN Auto-WireGuard Bot

Ce projet automatise la récupération de configurations WireGuard depuis l'interface web de PureVPN à l'aide de Playwright (Python). Il est conçu pour s'intégrer parfaitement à **systemd** afin que votre VPN ne démarre que lorsque la configuration est fraîchement mise à jour.

## ✨ Fonctionnalités

* **Automatisation Totale** : Connexion au compte PureVPN et génération du fichier `wg0.conf`.
* **Kill-Switch Natif** : Grâce à `systemd`, les services (Radarr, Sonarr, etc.) s'arrêtent si le VPN tombe.
* **Zéro Persistance** : Utilise un navigateur "headless" pour une sécurité maximale.
* **Dépendances Intelligentes** : WireGuard attend la fin du script avant de tenter une connexion.

## 🚀 Installation Rapide

Clonez le dépôt et lancez le script d'installation automatique :

```bash
git clone [https://github.com/jaeuwi74/purevpn_bot.git](https://github.com/jaeuwi74/purevpn_bot.git)
cd purevpn-bot
chmod +x install.sh
./install.sh