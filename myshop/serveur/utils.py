from json import JSONEncoder, JSONDecoder
from hashlib import sha3_256 as sha256
from pathlib import Path
import datetime
import platform
from _thread import *
import os
import re

from .exceptions import *

def run_path() -> str:
    """
    Retourne le répertoire de configuration de l'application en fonction du système d'exploitation.
    Crée le répertoire s'il n'existe pas.

    Returns:
        str: Chemin du répertoire de configuration.
    """
    if platform.system() == "Windows":
        config_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "myshop")
    else:
        config_path = os.path.expanduser("~/.config/myshop")
    config_dir = Path(config_path)
    if not config_dir.exists():
        config_dir.mkdir()

    return config_dir.as_posix()

def get_cookie() -> str:
    """
    Génère un cookie de session aléatoire.

    Returns:
        str: Cookie de session sous forme hexadécimale.
    """
    return os.urandom(32).hex()

def get_timestamp() -> str:
    """
    Retourne l'horodatage actuel au format 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        str: Horodatage actuel.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def message(data: tuple) -> tuple:
    """
    Encode un message en JSON et retourne le code associé.

    Args:
        data (tuple): Tuple contenant les données et le code.

    Returns:
        tuple: Données encodées en JSON et code.
    """
    d = data[0]
    code = data[1]
    return JSONEncoder().encode(d), code

def is_permited(role: str, action: str) -> bool:
    """
    Vérifie si un rôle donné a la permission d'effectuer une action spécifique.

    Args:
        role (str): Rôle de l'utilisateur (ex: 'admin', 'vendeur').
        action (str): Action à vérifier au format 'Base.Action'.

    Returns:
        bool: True si l'action est permise, False sinon.
    """
    perm_list = {
        "vendeur": {
            'Ventes': ['add'],
            'Stocks': ['all', 'get'],
            'Produits': ['all', 'get'],
            'Sessions': ['change', 'delete'],
            'Categories': ['all', 'get'],
            'Clients': ['add', 'get', 'all'],
            'Promotions': ['all', 'get']
        },
        "admin": {
            "Agents": ['all', 'get', 'add', 'change', 'delete'],
            "Users": ['all', 'get', 'add', 'change', 'delete'],
            "Produits": ['all', 'get', 'add', 'change', 'delete'],
            "Stocks": ['all', 'get', 'add', 'change', 'delete'],
            'Categories': ['all', 'get', 'add', 'change', 'delete'],
            'Sessions': ['all', 'get', 'add', 'change', 'delete'],
            'Logins': ['all', 'get', 'add', 'change', 'delete'],
            'Clients': ['all', 'get', 'add', 'change', 'delete'],
            'Arrivages': ['all', 'get', 'add', 'change', 'delete'],
            'Logs': ['all', 'delete'],
            'Ventes': ['all', 'get', 'add', 'change', 'delete'],
            'Promotions': ['all', 'get', 'add', 'change', 'delete'],
            'Notes': ['all', 'get', 'add', 'change', 'delete'],
            'Settings': ['all', 'get', 'add', 'change', 'delete']
        },
        'moniteur': {
            "Logs": ['all'],
            'Stocks': ['all'],
            'Produits': ['all'],
            'Users': ['all'],
            'Promotions': ['all'],
            'Notes': ['all']
        }
    }

    db, action = action.split(sep='.')
    p_db = perm_list.get(role)
    if p_db:
        p_list = p_db.get(db)
        if p_list:
            if action in p_list:
                return True

    return False

def sep_prix(prix: str) -> tuple:
    """
    Formate un prix en séparant les chiffres et la devise.

    Args:
        prix (str): Prix au format 'chiffres devise'.

    Returns:
        tuple: Nombre et devise séparés.

    Raises:
        MessagePersonnalise: Si le format du prix est incorrect.
    """
    prix_raw = prix.replace(' ', '')
    num = ''
    for i in prix_raw:
        if not i.isnumeric():
            break
        num += i

    dev = prix_raw.replace(num, '')
    if num == '':
        raise MessagePersonnalise('Veuillez insérer le prix au format correct')
    return num, dev

def valide_data(donnees: dict) -> bool:
    """
    Valide les données d'entrée en fonction d'un schéma prédéfini.

    Args:
        donnees (dict): Dictionnaire contenant les données à valider.

    Returns:
        bool: True si les données sont valides.

    Raises:
        TypeEntreException: Si un champ ne respecte pas les critères de validation.
    """
    schema = {
        "_id": {'type': int},
        "isform": {'type': bool}, "valide": {'type': bool},
        "produits_ids": {'type': list}, "marchandises": {'type': dict},
        "description": {'type': str},
        "sujet": {'type': str, 'max': 32, 'required': True},
        "label": {'type': str, 'max': 64, 'required': True},
        "code_barre": {'type': int},
        "quantite": {'type': int, 'required': True},
        "photo": {'type': str},
        "sexe": {'type': str, 'values': ['M', 'F'], 'required': True},
        "type": {'type': str, 'values': ['D', 'G'], 'required': True},
        "role": {'type': str, 'values': ['admin', 'moniteur', 'vendeur'], 'required': True},
        "username": {'type': str, 'max': 32, 'min': 3, 'required': True},
        "password": {'type': str, 'min': 6, 'required': True},
        "noms": {"type": str, "max": 62},
        "telephone": {"type": int, 'max': 24},
        "email": {"type": str, "regex": r"^[^@]+@[^@]+\.[^@]+$"},
        "from": {'type': str, "regex": r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$'},
        "to": {'type': str, "regex": r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$"}
    }
    for label, data in donnees.items():
        rules = schema.get(label)
        if not rules:
            if label.endswith('_id'):
                rules = schema.get('_id')
            else:
                continue

        if (data == '' and not rules.get('required')):
            continue

        for t, value in rules.items():
            if t == 'regex' and not re.match(value, data):
                raise TypeEntreException(label)
            if t == 'max' and len(data) > value:
                raise TypeEntreException(label)
            if t == 'min' and len(data) < value:
                raise TypeEntreException(label)
            if t == 'type':
                if value == int:
                    if not str(data).isnumeric():
                        raise TypeEntreException(label)
                    continue
                if not isinstance(data, value):
                    raise TypeEntreException(label)
            if t == 'values' and not (data in value):
                raise TypeEntreException(label)

    return True

def serialise(donnees: dict) -> dict:
    """
    Normalise et sécurise les données pour stockage ou transmission.

    Args:
        donnees (dict): Données à normaliser.

    Returns:
        dict: Données normalisées.
    """
    ret = {}
    for name, value in donnees.items():
        if value is None or value == '':
            continue

        if isinstance(value, (dict, list)):
            ret[name] = JSONEncoder().encode(value)
        elif isinstance(value, (datetime.date, datetime.datetime)):
            ret[name] = value.isoformat()
        elif isinstance(value, str):
            ret[name] = re.sub(r"[\"';]", '', value)
        else:
            ret[name] = str(value)

    return ret

def to_date(param: str) -> str:
    """
    Convertit une date au format 'JJ/MM/AAAA' en 'AAAA-MM-JJ'.

    Args:
        param (str): Date au format 'JJ/MM/AAAA'.

    Returns:
        str: Date au format 'AAAA-MM-JJ'.

    Raises:
        MessagePersonnalise: Si le format de la date est incorrect.
    """
    if not param:
        raise MessagePersonnalise('Le format de la date est incorrect')
    d = param.split('/')
    date = datetime.date(int(d[2]), int(d[1]), int(d[0]))
    return date.strftime('%Y-%m-%d')