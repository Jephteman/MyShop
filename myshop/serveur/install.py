import os
import socket
import base64
import platform
from .backends import *
from .utils import get_timestamp
from getpass import getpass
from colorama import init, Fore
from configparser import ConfigParser

init()

db_settings = database()
db_settings.connect(db='settings.db')

db_settings_instance =  Settingsdb(db_settings,first=True)

entry = {
    'host':'',
    'db_name':'MyShop.db',
    'db_username':'',
    'db_password':'',
    'connection_type':'',
    'salt':os.urandom(64).hex(),
    'back_action_time':18000
    }

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

def create_table(instance:database):
    print(Fore.BLUE + "[-] Creation des tables sur la base de donnees ")
    Logsdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Logs ")
    Loginsdb(instance,first=True, config=entry)
    print(Fore.BLUE + "     Creation de la table Logins ")
    Sessionsdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Sessions ")
    Agentsdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Agents ")
    Clientsdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Clients ")
    Categoriesdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Categories ")
    Produitsdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Produits ")
    Ventesdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Ventes ")
    Arrivagesdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Arrivages ")
    Promotionsdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Promotions ")
    Notesdb(instance,first=True)
    print(Fore.BLUE + "     Creation de la table Notes ")

    initiale_action(instance,config=entry)

    print(Fore.BLUE + "[+] Tables crees avec success ")

def insert_tb(instance,param):
    try:
        instance.add(param)
    except :
        instance.change(param)

    print(Fore.BLUE + f"[-] Insertion du {param.get('label')} dans la  base de donnees ")

def message():
    print(Fore.BLUE + """ 
        Vous etes sur le point d'installer la partie serveur du programme MyShop
        Ce serveur gereré tous ce qui concerne la base de donnee, les comptes utilisateurs,les permissions ainsi que les ressources
        """)

def run(**arg):
    config = ConfigParser()
    if platform.system() == "Windows":
        config_dir = Path(os.getenv('APPDATA')) / "myshop"
    else:
        config_dir = Path.home() / ".config" / "myshop"

    config_file = os.path.join(config_dir, "config.txt")

    config_file = config_dir / "config.txt"
    if config_file.exists():
        config.read(config_file._pattern_str)
        if config.has_section('SERVEUR'):
            if config.get('SERVEUR','IS_INSTALLED'): # nous sortons puisque l'installation a deja etait faite
                return
        else:
           config['SERVEUR'] = {}
           
    message()

    print('Veillez selectionner le mode de fonctionnement (local, distant) : ',end='')
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
    
    config['SERVEUR'] = {
        'network': get_secure_input("Adresse du serveur (default: 127.0.0.1) : ") or '127.0.0.1',
        'port': get_secure_input("Port (default: 8000) : ") or '8000',
        'IS_INSTALLED': 'yes'
    }

    print(Fore.BLUE + '[+] Enregistrement de donnéé dans la db')
    for label, value in entry.items():
        if not value:
            continue

        param = {'label':label,'value':value}
        insert_tb(db_settings_instance,param)

    print('[+] Test des informatios fournit')
    db_instance = database()

    try:
        db_instance.settings.update(db_settings_instance.all())
        db_instance.connect(db=entry.get('db_name'))
    except FileNotFoundError as e:
        print("[+] Le fichier de configuration n'a pas etre creer")
        exit(302)
    except Exception as e:
        print('Une exeption inconnu a lever')
    else:
        print("[+] Connection avec success a la db")


    create_table(db_instance)

    if not config.has_section('SERVEUR'):
        config['SERVEUR'] = {}
           

    # Créer le dossier de configuration s'il n'existe pas
    os.makedirs(config_dir, exist_ok=True)

    try:
        config['SERVEUR']['IS_INSTALLED'] = 'yes'
        with open(config_file,'a') as f:
            config.write(f)
    except Exception as e:
        print("Une erreur est survenue")
    else:
        print("[+] Installation terminée avec success")

    exit()

if __name__ == '__main__':
    run()

