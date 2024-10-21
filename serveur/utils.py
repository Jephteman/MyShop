"""

Un ensemble de func necessaire pour le fonctionement


"""
from json import JSONEncoder, JSONDecoder
from datetime import datetime
import os

def get_cookie():
    """Genere le cookie de session"""
    return os.urandom(32).hex()

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def message(data):
    d = data[0]
    code = data[1]
    return JSONEncoder().encode({"data":d,"code":code}),code
   
def is_permited(role,action:str):
    perm_list = {
        "vendeur":{
            'Ventes':['add'],
            'Stocks':['all'],
            'Produits':['all'],
            'Sessions':['change','delete'],
            'Categories':['all'],
            'Clients':['add','change','all']
            },
        "admin":{
            "Agents":['add','delete','change','all'],
            "Users":['add','delete','change','all'],
            "Produits":['add','delete','change','all'],
            "Stocks":['add','delete','change','all'],
            'Categories':['add','delete','change','all'],
            'Sessions':['add','delete','change','all'],
            'Logins':['add','change','all','delete'],
            'Clients':['add','change','all'],
            'Arrivages':['add','delete','all'],
                'Logs':['all','delete'],
                'Ventes':['all','add','delete','change']
            },
        'moniteur':{
            "Logs":['all'],
            'Stocks':['all'],
            'Produits':['all'],
            'Users':['all']
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
