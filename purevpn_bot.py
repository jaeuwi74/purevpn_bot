import os
import time
from playwright.sync_api import sync_playwright
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv() # Charge le fichier .env

# --- CONFIGURATION ---
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SAVE_PATH = "wg0.conf"
DEST_PATH = "/etc/wireguard/wg0.conf"
SCREENSHOT_DIR = "debug_steps"
DEBUG = False

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_ss(page, name):
    path = f"{SCREENSHOT_DIR}/{name}.png"
    time.sleep(0.5)
    print(name)
    if DEBUG:
        try:
            page.screenshot(path=path)
            print(f"   [📸 Screenshot] {path}")
        except Exception as e:
            print(f"   [!] Erreur capture {name}: {e}")

def cleanup_before_start():
    """Supprime les anciens fichiers pour éviter les faux positifs"""
    print(f"[{time.strftime('%H:%M:%S')}] 🧹 Nettoyage des anciens fichiers...")
    
    # Supprime le fichier local
    if os.path.exists(SAVE_PATH):
        try:
            os.remove(SAVE_PATH)
            print(f"   > Ancien fichier local '{SAVE_PATH}' supprimé.")
        except Exception as e:
            print(f"   [!] Erreur suppression local: {e}")

    # Supprime le fichier système (nécessite sudo)
    try:
        subprocess.run(["sudo", "rm", "-f", DEST_PATH], check=True)
        print(f"   > Ancien fichier système '{DEST_PATH}' supprimé.")
    except Exception as e:
        print(f"   [!] Erreur suppression système: {e}")

def download_purevpn_config():
    """Gère toute la partie navigation et téléchargement sur PureVPN"""
    print(f"[{time.strftime('%H:%M:%S')}] 🌐 Démarrage du téléchargement PureVPN...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            # 1. LOGIN
            page.goto("https://my.purevpn.com/v2/login", wait_until="load")
            take_ss(page, "01_page_login")
            page.type('input#loginId', EMAIL, delay=50)
            page.type('input[name="password"]', PASSWORD, delay=50)
            take_ss(page, "02_identifiants_saisis")
            page.click('button.fusiona-submit')
            time.sleep(5)
            take_ss(page, "03_apres_clic_login")

            # 2. NAVIGATION CONFIG
            page.goto("https://my.purevpn.com/v2/dashboard/manual-config", wait_until="networkidle")
            time.sleep(5)
            take_ss(page, "04_page_config")

            # 3. FILTRE PF
            page.click("#PF", force=True)
            time.sleep(5)
            take_ss(page, "05_filtre_PF_active")

            # 4. SCROLL ET DEPLOIEMENT FRANCE
            page.mouse.wheel(0, 800)
            time.sleep(3)
            take_ss(page, "06_avant_clic_france")
            page.get_by_text("France", exact=True).first.click(force=True)
            time.sleep(5) 
            take_ss(page, "07_villes_deployees")

            # 5. CLIC SUR PARIS
            bloc_paris = page.locator(".countryCity", has_text="Paris")
            btn_paris = bloc_paris.locator(".cityButton")
            page.evaluate(f"document.querySelector('.countryCity').scrollIntoView();")
            time.sleep(2)
            take_ss(page, "08_avant_clic_paris")
            btn_paris.dispatch_event("click")
            
            # 6. POPUP CONFIG
            time.sleep(5)
            take_ss(page, "09_popup_ouvert")
            page.select_option('select[name="select"]', value="WireGuard")
            time.sleep(3)
            page.select_option('#device', value="linux")
            time.sleep(5)
            take_ss(page, "10_popup_pret")

            # 7. TÉLÉCHARGEMENT
            with page.expect_download(timeout=60000) as download_info:
                page.click('button[data-qamarker="generateWGConf"]', force=True)
            
            download = download_info.value
            download.save_as(SAVE_PATH)
            
            if os.path.exists(SAVE_PATH) and os.path.getsize(SAVE_PATH) > 0:
                print(f"✅ Fichier téléchargé localement.")
                take_ss(page, "11_final")
                browser.close()
                return True
            else:
                raise Exception("Fichier vide ou manquant.")

        except Exception as e:
            print(f"❌ Erreur Web : {e}")
            take_ss(page, "99_ERREUR_WEB")
            browser.close()
            return False

def deploy_to_system():
    """Gère uniquement la copie et les permissions système"""
    print(f"[{time.strftime('%H:%M:%S')}] 🚀 Déploiement système vers {DEST_PATH}...")
    try:
        if not os.path.exists(SAVE_PATH):
            print("❌ Erreur : Aucun fichier source à copier.")
            return False

        # Copie et permissions
        subprocess.run(["sudo", "cp", SAVE_PATH, DEST_PATH], check=True)
        subprocess.run(["sudo", "chmod", "600", DEST_PATH], check=True)
        print(f"✅ Fichier déployé et sécurisé dans {DEST_PATH}")
        return True
    except Exception as e:
        print(f"❌ Erreur Système : {e}")
        return False

if __name__ == "__main__":
    print(f"\n--- DÉMARRAGE DU SCRIPT ---")
    
    # 0. Étape de nettoyage initial
    cleanup_before_start()
    
    # 1. Étape Web
    if download_purevpn_config():
        # 2. Étape Système
        if deploy_to_system():
            print(f"--- MISSION TERMINÉE AVEC SUCCÈS ---")
            sys.exit(0)
        else:
            print("❌ Échec lors du déploiement.")
            sys.exit(1)
    else:
        print("❌ Échec lors du téléchargement.")
        sys.exit(1)