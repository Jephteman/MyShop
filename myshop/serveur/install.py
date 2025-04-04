import os
import platform
import base64, pathlib
from .backends import *
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
    'connetion_type':'',
    'salt':os.urandom(64).hex(),
    'back_action_time':18000
    }

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
    message()

    print('Veillez selectionner le mode de fonctionnement (local, distant) : ',end='')
    t = ''
    while t not in ['local','distant']:
        t = input('').lower()
        entry.update({'connection_type':t})

    d = input('le nom de la base de donne (default: MyShop) : ')

    if d:
        entry.update({'db_name':d})

    if t == 'distant':
        host = input('IP/Nom de domaine de la db :')
        entry.update({'host':host})
        user = input("nom d'utilisateur de la db : ")
        entry.update({'db_username':user})
        passwd = input('Mot de pass de la db : ')
        entry.update({'db_password':passwd})
    
    print('Veillez entrer le nom de la bourtique (obligatoire)')
    name = input('Nom :' )
    if not name:
        name = input('Nom :' )
    entry.update({'boutique':name})

    print('Veillez entrer la description de la bourtique')
    desc = input('Description  :' )
    entry.update({'description':desc})

    print('Veillez entrer le contact de la boutique')
    contact = input('Contact :' )
    entry.update({'contact':contact})

    print('Veillez entrer le chemin vers le logo de la bourtique (optionel)')
    logo = input('Chemin du logo  :' )
    if logo:
        with open(logo,'rb') as f:
            logo = f.read()
            logo = base64.encodebytes(logo)
            logo = logo.decode()
    entry.update({'logo':logo})

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

    config = ConfigParser()
    if not config.has_section('SERVEUR'):
        config['SERVEUR'] = {}
        
    # Détecter le système d'exploitation
    if platform.system() == "Windows":
        config_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "myshop")
    else:
        config_dir = os.path.expanduser("~/.config/myshop")

    config_file = os.path.join(config_dir, "config.txt")

    # Créer le dossier de configuration s'il n'existe pas
    os.makedirs(config_dir, exist_ok=True)

    print("Veilez entrer l'addresse vers du serveur ")
    config['SERVEUR']['network'] = input("Addresse (127.0.0.1): ")
    if not config['SERVEUR']['network']:
        config['SERVEUR']['network'] = '127.0.0.1'

    print("Veilez entrer le port ")
    config['SERVEUR']['port'] = input("Port (8000): ")
    if not config['SERVEUR']['port']:
        config['SERVEUR']['port'] = '8000'

    try:
        config['SERVEUR']['IS_INSTALLED'] = 'yes'
        with open(config_file,'a') as f:
            config.write(f)
    except Exception as e:
        print("Une erreur est survenue")
    else:
        print("[+] Installation terminée avec success")

    exit(0)

if __name__ == '__main__':
    run()

