import os 
import socket
import platform
import base64
import secrets
from pathlib import Path
from configparser import ConfigParser
from colorama import init, Fore
from getpass import getpass

init()

def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def get_secure_input(prompt, is_password=False):
    if is_password:
        return getpass(prompt)
    return input(prompt).strip()

def create_config_file(config, config_file):
    try:
        with open(config_file, 'w') as f:
            config.write(f)
        os.chmod(config_file, 0o600)  # Restrict permissions
    except Exception as e:
        print(Fore.RED + f"Erreur lors de la création du fichier de configuration : {e}")
        return False
    return True

def run():
    print(Fore.BLUE + "Bienvenue dans l'installation de MyShop")

    entry = {
        'host': '',
        'db_name': 'MyShop.db',
        'db_username': '',
        'db_password': '',
        'connection_type': '',
        'salt': secrets.token_hex(64),
        'back_action_time': 18000
    }

    # Mode de fonctionnement
    while entry['connection_type'] not in ['local', 'distant']:
        entry['connection_type'] = get_secure_input("Mode de fonctionnement (local, distant) : ").lower()

    # Nom de la base de données
    db_name = get_secure_input("Nom de la base de données (default: MyShop) : ")
    if db_name:
        entry['db_name'] = db_name

    # Configuration distante
    if entry['connection_type'] == 'distant':
        while not validate_ip(entry['host']):
            entry['host'] = get_secure_input("IP/Nom de domaine de la DB : ")
        entry['db_username'] = get_secure_input("Nom d'utilisateur de la DB : ")
        entry['db_password'] = get_secure_input("Mot de passe de la DB : ", is_password=True)

    # Configuration de la boutique
    entry['boutique'] = get_secure_input("Nom de la boutique (obligatoire) : ")
    entry['description'] = get_secure_input("Description de la boutique : ")
    entry['contact'] = get_secure_input("Contact de la boutique : ")

    # Logo
    logo_path = get_secure_input("Chemin vers le logo de la boutique (optionnel) : ")
    if logo_path and Path(logo_path).is_file():
        with open(logo_path, 'rb') as f:
            entry['logo'] = base64.b64encode(f.read()).decode()

    # Configuration du serveur
    config = ConfigParser()
    config['SERVEUR'] = {
        'network': get_secure_input("Adresse du serveur (default: 127.0.0.1) : ") or '127.0.0.1',
        'port': get_secure_input("Port (default: 8000) : ") or '8000',
        'IS_INSTALLED': 'yes'
    }

    # Détecter le système d'exploitation
    if platform.system() == "Windows":
        config_dir = Path(os.getenv('APPDATA')) / "myshop"
    else:
        config_dir = Path.home() / ".config" / "myshop"

    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.txt"

    if create_config_file(config, config_file):
        print(Fore.GREEN + "[+] Installation terminée avec succès")
    else:
        print(Fore.RED + "[-] Échec de l'installation")
