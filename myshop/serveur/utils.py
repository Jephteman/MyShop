from json import JSONEncoder, JSONDecoder
from hashlib import sha3_256 as sha256
from pathlib import Path
import datetime, platform
from _thread import *
import os
import re

from .exceptions import *

def run_path():
    """
        Nous retourne le repetoire de parametre
    """
    if platform.system() == "Windows":
        config_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "myshop")
    else:
        config_path = os.path.expanduser("~/.config/myshop")
    config_dir = Path(config_path)
    if not config_dir.exists():
        config_dir.mkdir()

    return config_dir.as_posix()

def get_cookie():
    """Genere le cookie de session"""
    return os.urandom(32).hex()

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def message(data):
    d = data[0]
    code = data[1]
    return JSONEncoder().encode(d),code
   
def is_permited(role,action:str):
    perm_list = {
        "vendeur":{
            'Ventes':['add'],
            'Stocks':['all','get'],
            'Produits':['all','get'],
            'Sessions':['change','delete'],
            'Categories':['all','get'],
            'Clients':['add','get','all'],
            'Promotions':['get','all'],
            'Promotions':['all','get']
            },
        "admin":{
            "Agents":['all','get','add','change','delete'],
            "Users":['all','get','add','change','delete'],
            "Produits":['all','get','add','change','delete'],
            "Stocks":['all','get','add','change','delete'],
            'Categories':['all','get','add','change','delete'],
            'Sessions':['all','get','add','change','delete'],
            'Logins':['all','get','add','change','delete'],
            'Clients':['all','get','add','change','delete'],
            'Arrivages':['all','get','add','change','delete'],
            'Logs':['all','delete'],
            'Ventes':['all','get','add','change','delete'],
            'Promotions':['all','get','add','change','delete'],
            'Notes':['all','get','add','change','delete'],
            'Settings':['all','get','add','change','delete']
            },
        'moniteur':{
            "Logs":['all'],
            'Stocks':['all'],
            'Produits':['all'],
            'Users':['all'],
            'Promotions':['all'],
            'Notes':['all']

            }
        }

    db,action = action.split(sep='.')
    p_db = perm_list.get(role)
    if p_db:
        p_list = p_db.get(db)
        if p_list:
            if action in p_list:
                return True
            
    return False

def sep_prix(prix:str):
    """ Formalution du prix dans le format 'chiffres devise' """
    prix_raw =  prix.replace(' ','')
    num = ''
    for i in prix_raw:
        if not i.isnumeric():
            break
        num += i

    dev = prix_raw.replace(num,'')
    if num == '':
        raise MessagePersonnalise('Veillez inserer le prix au format correcte')
    return num,dev

def valide_data(donnees):
    schema = {
        "_id": {'type':int},
        "isform":{'type':bool},"valide":{'type':bool},
        "produits_ids":{'type':list},"marchandises":{'type':dict},
        "description":{'type':str},
        "sujet":{'type':str,'max':32,'required':True},
        "label":{'type':str,'max':64,'required':True},
        "code_barre":{'type':int},
        "quantite":{'type':int,'required':True},
        "photo":{'type':str},
        "sexe":{'type':str,'values':['M','F'],'required':True},
        "type":{'type':str,'values':['D','G'],'required':True},
        "role":{'type':str,'values':['admin','moniteur','vendeur'],'required':True},
        "username":{'type':str,'max':32,'min':3,'required':True},
        "password":{'type':str,'min':6,'required':True},
        "noms": {"type": str, "max": 62},
        "telephone": {"type": int,'max':24},
        "email": {"type": str, "regex": r"^[^@]+@[^@]+\.[^@]+$"},
        #"date":{'type':str,"regex":r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}'},
        "from":{'type':str,"regex":r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$'},
        "to":{'type':str,"regex":r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$"}
    }
    for label, data in donnees.items():
        rules = schema.get(label)
        if not rules :
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
            if t == 'type' :
                if value == int:
                    if not str(data).isnumeric():
                        raise TypeEntreException(label)
                    continue
                if not isinstance(data, value):
                    raise TypeEntreException(label)
            if t == 'values' and not (data in value):
                raise TypeEntreException(label)

    return True

def serialise(donnees): # pas acheve 
    raise NotImplemented
    """   
        s'assure que les donnees ne sont pas dangeré pour etre executer
    """
    ret = {}

    for name , value in donnees.items():
        if not value:
            continue
        ret.update({name:value})
    return ret

def to_date(param):
    if not param:
        raise MessagePersonnalise('Le formant de la date est incorrecte')
    d = param.split('/')
    date = datetime.date(int(d[2]), int(d[1]) ,int(d[0]) )
    return date.strftime('%Y-%m-%d')    