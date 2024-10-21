import os
from sqlalchemy import create_engine, text

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
            self.type = arg['type']
            self.connect(arg)

    def check(self,type_,arg:dict):
        """ Verifie si le parametre fournit pourrons tenir pour le fonctionnement du programme """
        if type_ == 'local':
            try:
                create_engine("sqlite:///{}".format(os.path.join(arg['path'],arg['db_name']))).connect()
                return True
            except : 
                return False
        else:
            try:
               create_engine("mysql+mysqlconnector://{}:{}@{}/{}".format(arg['username'],arg['passwd'],arg['host'],arg['db_name'])).connect()
               return True
            except :
                return False

    def connect(self,arg):
        if arg['type'] == 'remove':
            self.type = 'remove'
            self.db =  create_engine("mysql+mysqlconnector://{}:{}@{}/{}".format(arg['username'],arg['passwd'],arg['host'],arg['db_name']))
        elif arg['type'] == 'local':
            self.db = create_engine("sqlite:///{}".format(os.path.join(arg['path'],arg['db_name'])))
            self.type = 'local'

    def cursor(self):
        return self.db.connect()

class Ventes(database):
    def __init__(self,cred):
        super().__init__()
        self.connect(cred)
        cursor = self.cursor()
        query = "create table if not exists ventes(num Text,nom Text,marchandise Text, piece Integer,type Text, date Text)"
        cursor.execute(text(query)) #utiliser pour l'inventaire et la journalisation
        cursor.close()

    def insert_vente(self,num,nom,marchandise,piece,type_,date):
        """insert les donnees dans la table ventes"""
        data = {'num':num,'nom':nom,'marchandise':marchandise,'piece':piece,'type_':type_,'date':date}
        cursor = self.cursor()
        cursor.execute(text("insert into ventes values (:num,:nom,:marchandise,:piece,:type_,:date)"),data)

        if type_ == 'achat':
            cursor.execute(text("update stock set quantite = quantite - :piece where marchandise = :marchandise;"),{'piece':piece,'marchandise':marchandise})
        else: 
            cursor.execute(text("update stock set quantite = quantite + :piece where marchandise = :marchandise;"),{'piece':piece,'marchandise':marchandise})
        
        cursor.commit()
        cursor.close()

    def get_vente(self,i):
        """renvoi l element vente"""
        cursor = self.cursor()
        l = None
        for i in cursor.execute(text("select * from ventes where num = :num;"),{'num':i}):
            l = i
        cursor.close()
        return l

    def list_vente(self): # je pense qu'il faut s'y prendre autrement
        """renvoi les elements de la tables ventes"""
        cursor = self.cursor()
        ventes = []
        for num, nom, marc, piece,type_, date in cursor.execute(text("select * from ventes")):
            ventes.append([num, nom, marc, piece,type_, date ])
        cursor.close()
        return ventes

    def get_last_num(self):
        """renvoi le num du dernier element dans la table ventes"""
        cursor = self.cursor()
        n = 0
        for num in cursor.execute(text('select num from ventes;')):
            n = num
    
        cursor.close()

        try:
            return int(n[0])
        except:
            return n

    def num_exist(self,num):
        """verifie si un num existe deja dans la table ventes"""
        cursor = self.cursor()
        j = (0,0)
        for i in cursor.execute(text("select num from ventes where num = :num"),{'num':num}):
            j = i

        if j[0] == 0:
            return False
        return True

class Stock(database):
    def __init__(self,creds):
        super().__init__()
        self.connect(creds)
        cursor = self.cursor()
        cursor.execute(text("create table if not exists stock(marchandise Text, prix Text, quantite integer);")) # 
        cursor.execute(text("create table if not exists arrivages(marchandise Text, prix Text, quantite integer, date Text);"))
        cursor.close()

    def insert_stock(self,march,prix,n,date):
        cursor = self.cursor()
        cursor.execute(text("update stock set prix = :prix where marchandise = :march;"),{'prix':prix,'march':march})
        cursor.execute(text("update stock set quantite = quatite + :n where marchandise = :march;"),{'n':int(n),'march':march})
        cursor.execute(text("insert into arrivages(:march , :prix, :q, :date);",{'march':march,'prix':prix,'q':n,'date':date}))
        cursor.commit()
        cursor.close()

    def get_stock_all(self):
        """Nous retourne le stock de marchandise dans la db"""
        cursor = self.cursor()
        l = cursor.execute(text('select * from stock'))
        cursor.close()
        return l
    
    def list_produits(self):
        """listes de produits"""
        cursor = self.cursor()
        l = []
        for i in cursor.execute(text("select marchandise from stock")):
            l.append(i[0])
        cursor.close()
        return l
    
    def get_stock(self,march):
        """retourne le stock d'une marchandise"""
        cursor = self.cursor()
        n = 0
        for i in cursor.execute(text("select quantite from stock where marchandise = :march;"),{'march':march}):
            n = i[0]
        cursor.close()
        return n

    def insert_arrivage(self,marchandise,prix, quantite,date):
        """insert le sentree dans la tables arrivages"""
        cursor = self.cursor()
        cursor.execute(text("insert into arrivages values (:march,:prix,:n,:date);"),{'march':marchandise,'prix':prix,'n':int(quantite),'date':date})
        if marchandise in self.list_produits():
            cursor.execute(text("update stock set prix = :prix where marchandise = :march;"),{'prix':prix,'march':marchandise})
            cursor.execute(text("update stock set quantite = quantite + :q where marchandise = :march;"),{'q':int(quantite),'march':marchandise})
        else:
            cursor.execute(text("insert into stock values (:march,:prix,:q);"),{'march':marchandise,'prix':prix,'q':int(quantite)})
        cursor.commit()
        cursor.close()

    def insert_produit(self,produit):
        """inserer un nouveau produit"""
        cursor = self.cursor()
        cursor.execute(text("insert into stock values (:p,0,0)"),{'p':produit})
        cursor.commit()
        cursor.close()

    def get_prix(self,march):
        cursor = self.cursor()
        prix = 0
        for i in cursor.execute(text("select prix from stock where marchandise = :march;"),{'march':march}):
            prix = i[0]
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

