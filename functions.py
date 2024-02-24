import sqlite3
import os
from sqlalchemy import create_engine

def is_install():
    try:
        f = open('.config.txt','r').read()
        if len(f) > 2:
            return f
        return False
    except:
        return False

class database:
    def __init__(self,**arg):
        """Initialisation """
        if len(arg) > 1:
            self.connect(arg)

    def check(self,type_,arg:dict):
        """ Verifie si le parametre fournit pourrons tenir pour le fonctionnement du programme """
        if type_ == 'local':
            try:
                sqlite3.connect(os.path.join(arg['path'],arg['name']))
                return True
            except : 
                return False
        else:
            try:
                x = create_engine("mysql+mysqlconnector://{}:{}@{}/{}".format(arg['username'],arg['passwd'],arg['host'],arg['db_name'])).connect()
                return True
            except :
                return False

    def connect(self,arg):
        if arg['type'] == 'remove':
            self.db =  create_engine("mysql+mysqlconnector://{}:{}@{}/{}".format(arg['username'],arg['passwd'],arg['host'],arg['db_name']))
        elif arg['type'] == 'local':
            self.db = sqlite3.connect(os.path.join(arg['path'],arg['db_name']))

class Ventes(database):
    def __init__(self,cred):
        super().__init__()
        self.connect(cred)
        cursor = self.db.cursor()
        cursor.execute("create table if not exists ventes(num ,nom ,marchandise, piece,type, date)") #utiliser pour l'inventaire et la journalisation
        cursor.close()

    def insert_vente(self,num,nom,marchandise,piece,type_,date):
        """insert les donnees dans la table ventes"""
        cursor = self.db.cursor()
        cursor.execute("insert into ventes values (?,?,?,?,?,?)",(str(num),nom,marchandise,piece,type_,date))

        if type_ == 'achat':
            cursor.execute("update stock set quantite = quantite - ? where marchandise = ?",(piece,marchandise,))
        else: 
            cursor.execute("update stock set quantite = quantite + ? where marchandise = ?",(piece,marchandise,))
        
        self.db.commit()
        cursor.close()

    def get_vente(self,i):
        """renvoi l element vente"""
        cursor = self.db.cursor()
        l = cursor.execute("select * from ventes where num = ?",(i)).fetchall()
        cursor.close()
        return l

    def list_vente(self): # je pense qu'il faut s'y prendre autrement
        """renvoi les elements de la tables ventes"""
        cursor = self.db.cursor()
        ventes = []
        for num, nom, marc, piece,type_, date in cursor.execute("select * from ventes"):
            ventes.append([num, nom, marc, piece,type_, date ])
        cursor.close()
        return ventes

    def get_last_num(self):
        """renvoi le num du dernier element dans la table ventes"""
        cursor = self.db.cursor()
        n = 0
        for num in cursor.execute('select num from ventes'):
            n = num
    
        cursor.close()

        try:
            return int(n[0])
        except:
            return n

    def num_exist(self,num):
        """verifie si un num existe deja dans la table ventes"""
        cursor = self.db.cursor()
        j = (0,0)
        for i in cursor.execute("select num from ventes where num = ?",(num)):
            j = i

        if j[0] == 0:
            return False
        return True

class Stock(database):
    def __init__(self,creds):
        super().__init__()
        self.connect(creds)
        cursor = self.db.cursor()
        cursor.execute("create table if not exists stock(marchandise, prix, quantite integer)") # 
        cursor.execute("create table if not exists arrivages(marchandise, prix, quantite integer, date)")
        cursor.close()

    def insert_stock(self,march,prix,n,date):
        cursor = self.db.cursor()
        cursor.execute("update stock set prix = ? where marchandise = ?",(prix,march,))
        cursor.execute("update stock set quantite = quatite + ? where marchandise = ?",(n,march,))
        self.db.commit()
        cursor.close()

    def get_stock_all(self):
        """Nous retourne le stock de marchandise dans la db"""
        cursor = self.db.cursor()
        cursor.execute('select * from stock')
        l = cursor.fetchall()
        cursor.close()
        return l
    
    def list_produits(self):
        """listes de produits"""
        cursor = self.db.cursor()
        l = []
        for i in cursor.execute("select marchandise from stock"):
            l.append(i[0])
        cursor.close()
        return l
    
    def get_stock(self,march):
        """retourne le stock d'une marchandise"""
        cursor = self.db.cursor()
        n = 0
        for i in cursor.execute("select quantite from stock where marchandise == ?",(march,)):
            n = i[0]
        cursor.close()
        return n

    def insert_arrivage(self,marchandise,prix, quantite,date):
        """insert le sentree dans la tables arrivages"""
        cursor = self.db.cursor()
        cursor.execute("insert into arrivages values (?,?,?,?)",(marchandise,prix,quantite,date))
        if marchandise in self.list_produits():
            cursor.execute("update stock set prix = ? where marchandise = ?",(prix,marchandise))
            cursor.execute("update stock set quantite = quantite + ? where marchandise = ?",(quantite,marchandise))
        else:
            cursor.execute("insert into stock values (?,?,?)",(marchandise,prix,quantite))
        self.db.commit()
        cursor.close()

    def insert_produit(self,produit):
        """inserer un nouveau produit"""
        cursor = self.db.cursor()
        cursor.execute("insert into stock values (?,?,?)",(produit,0,0))
        self.db.commit()
        cursor.close()

    def get_prix(self,march):
        cursor = self.db.cursor()
        prix = 0
        for p in cursor.execute("select prix from stock where marchandise == (?);",(march,)):
            prix = p[0]
        cursor.close()
        return prix

def ret_prix_int(p):
    """Return le prix entant que nombre"""
    n = '0'
    for i in p:
        if i.isnumeric():
            n+=i
    return int(n)

def ret_prix_fourchette(p):
    """retourne la fourchette de prix"""
    f = ''
    for i in p:
        if not i.isnumeric():
            f+=i
    return f

