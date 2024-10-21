from sqlalchemy import create_engine, text
from utils import get_cookie, get_timestamp
import time
from exceptions import *


class database:
    def __init__(self,**arg):
        """Initialisation """
        self.db = None
        if len(arg) > 1:
            self.type = arg['type']
            self.connect(arg)

    def check(self,host,user,passwd,db_name,net:str='local'):
        """ Verifie si le parametre fournit pourrons tenir pour le fonctionnement du programme """
        if net == 'local':
            try:
                create_engine("sqlite:///{}".format(db_name)).connect()
                return True
            except : 
                return False
        else:
            try:
               create_engine("mysql+mysqlconnector://{}:{}@{}/{}".format(user,passwd,host,db_name)).connect()
               return True
            except :
                return False

    def connect(self,host,user,passwd,db_name,net:['local','remote']='local'):
        if net == 'remote':
            self.type = 'remote'
            self.host = host
            self.username = user
            self.passwd = passwd
            self.db_name = db_name
            self.autoincrement = 'auto_increment'

            self.db =  create_engine("mysql+mysqlconnector://{}:{}@{}/{}".format(user,passwd,host,self.db_name))
        elif net == 'local':
            self.db_name = db_name

            self.db = create_engine("sqlite:///{}".format(self.db_name))
            self.type = 'local'
            self.autoincrement = 'autoincrement'

        else:
            raise Exception('un probleme avec le mode de connection de la db')
        
    def cursor(self):
        """retourne le cursor"""
        return self.db.connect()

class Logsdb():
    def __init__(self,instance:database,first=False):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """
            create table if not exists Logs(
                log_id integer primary key {},
                date datetime,
                message varchar(64),
                action varchar(16)    
            )""".format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.commit()
            cursor.close()

    def add(self,param):
        """ajout d'un nouveau log"""
        cursor = self.instance.cursor()
        query = "insert into Logs(date,message,action) values(:date,:message,:action)"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

class Loginsdb():
    def __init__(self,instance:database,first=False):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """create table if not exists Logins(
                login_id integer primary key {},
                username char(32) unique not null,
                password char(64) not null,
                role char(8) not null,
                statut integer(1) not null default 1)
            """.format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.commit()
            cursor.close()

    def check(self,param):
        cursor = self.instance.cursor()
        query = "select login_id,statut from Logins where username == :username and password == :password;"
        idt = None
        for i in cursor.execute(text(query),param):
            idt = i._asdict()

        if idt:
            if idt['statut'] == 0:
                raise UtilisateurBloquerException(param.get('username'))
        return idt
    
    def reset_passwd(self,param):
        if not param.get('password','invalid1') == param.get('confirm_password','invalid'):
            raise MessagePersonnalise('les mots de passes doivent etre identiques')
        

        cursor = self.instance.cursor()
        query = """update Logins set password == :password where login_id == :login_id"""
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def add(self,param:dict):
        cursor = self.instance.cursor()
        query = "insert into Logins(username,password,role) values(:username,:password,:role)"
        cursor.execute(text(query),param)
        cursor.commit()
        id = None
        for i in cursor.execute(text('select login_id,role,statut from Logins where username == :username and password == :password'),param):
            id = i._asdict()

        cursor.close()
        return id

    def change(self,param):
        """
        {
            'username':str,
            'role':str,
            'login_id';str
        }
        """
        cursor = self.instance.cursor()
        query = """update Logins set username = :username, role = :role where login_id == :login_id;"""
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()
    
    def delete(self,param):
        """
        {
            'login_id':int
        }
        """
        cursor = self.instance.cursor()
        query = "delete from Logins where login_id == :login_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()
    
    def all(self,param=None):
        cursor = self.instance.cursor()
        query = text("select login_id ,username, role, statut from Logins;")
        data = []
        for i in cursor.execute(query):
            data.append(i._asdict())

        cursor.close()
        return data
    
    def get(self,param):
        """
        {
            'login_id':int
        }
        """
        cursor = self.instance.cursor()
        query = "select login_id,username,role,statut from Logins where login_id == :login_id;"
        res = None
        for i in cursor.execute(text(query),param):
            res = i._asdict()

        cursor.close()
        return res

class Sessionsdb():
    def __init__(self,instance:database,first=False):
        self.db_instance = instance
        if first:
            cursor = self.db_instance.cursor()
            query ="""create table if not exists Sessions(
                       session_id integer primary key {},
                       date datetime not null,
                       cookies char(32) unique not null,
                       statut int unsigned default 1,
                       login_id integer ,
                       ip_addr varchar(16),
                       foreign key (login_id) references Logins(login_id) )""".format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.commit()
            cursor.close()

    def add(self,param):
        """
            {
                'login_id':int
            }
        """
        cursor = self.db_instance.cursor()
        param['cookie'] = get_cookie()
        param['date'] = get_timestamp()
        cursor.execute(text("insert into Sessions(date,cookies,login_id,ip_addr) values(:date,:cookie,:login_id,:ip_addr)"),param)
        cursor.commit()
        cursor.close()
        return {'sessions':param['cookie']}
    
    def all(self,param=None):
        data = []
        cursor = self.db_instance.cursor()
        
        for i in cursor.execute(text("select session_id,date,statut,login_id,ip_addr from Sessions")):
            data.append(i._asdict())

        cursor.close()
        return data
    
    def delete(self,param):
        """
        {
            'session_id':int
        }
        """
        cursor = self.db_instance.cursor()
        cursor.execute(text("delete from Sessions where session_id == :session_id"),param)
        cursor.commit()
        cursor.close()

    def change(self,param):
        """
            {
                'session_id':int,
                'statut':int
                
            }
        """
        cursor = self.db_instance.cursor()
        cursor.execute(text("update Sessions set statut = 0 where session_id == :session_id"),param)
        cursor.commit()
        cursor.close()

    def check(self,cookie:dict):
        cursor = self.db_instance.cursor()
        query = text("select login_id from Sessions where cookies == :c")
        user_id = None
        for i in cursor.execute(query,{'c':cookie.get('sessions','')}):
            user_id = i._asdict()

        cursor.close()
        return user_id

class Agentsdb():
    def __init__(self, instance:database,first=False):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """create table if not exists Agents(
                login_id integer primary key {},
                noms char(32) not null,
                addr char(32) ,
                telephone integer(15),
                email char(32),
                photo Text ,foreign key (login_id) references Logins(login_id));""".format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.commit()
            cursor.close()

    def add(self,param):
        """
            {
                'noms':str,
                'addr':str,
                'login_id':int,
                'telephone':str null,
                'email':str null,
                'photo':
            }
        """
        cursor = self.instance.cursor()
        query = "insert into Agents(noms, addr, login_id, telephone, email,photo) values(:noms,:addr,:login_id,:telephone,:email,:photo)"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def delete(self,param):
        """
            {
                "login_id":int
            }
        """
        cursor = self.instance.cursor()
        query = "delete from Agents where login_id == :login_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        Loginsdb(self.instance).delete(param)
        cursor.close()

    def change(self,param):
        """
            {
                'login_id':int,
                'nom':str
                'addr':str
                'telephone':str,
                'email':str,
                'photo':str
                
            }
        """
        cursor = self.instance.cursor()
        query = "update Agents set noms = :noms, addr = :addr, telephone = :telephone, email = :email,photo = :photo where login_id == :login_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def all(self,param=None):
        cursor = self.instance.cursor()
        query = "select * from Agents"
        data = []
        for i in cursor.execute(text(query)):
            data.append(i._asdict())

        cursor.close()
        return data
    
    def get(self,param):
        """
        {
            'login_id':int
        }
        """
        cursor = self.instance.cursor()
        query = "select * from Agents where login_id == :login_id"
        data = []
        for i in cursor.execute(text(query),param):
            data.append(i._asdict())

        cursor.close()
        return data

class Nationalitesdb():
    def __init__(self,instance:database,first=False):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """create table if not exists Nationalites(
                nationalite_id integer primary key {},
                label char(24) not null unique
            )""".format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.commit()
            cursor.close()

    def add(self,param):
        """
            {
                'label':str
            }
        """
        cursor = self.instance.cursor()
        query = "insert into Nationalites (label) values (:label);"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def change(self,param):
        """
            {
                'nationalite_id':int,
                'label':str
            }
        """
        cursor = self.instance.cursor()
        query = "update Nationalites set label = :label where nationalite_id == :nationalite_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def delete(self,param):
        """
            {
                'nationalite_id':int
            }
        """
        cursor = self.instance.cursor()
        query = "delete Nationalites where nationalite_id == :nationalite_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def all(self,param=None):
        cursor = self.instance.cursor()
        query = text("select * from Nationalites;")
        data = []
        for l in cursor.execute(query):
            data.append(l._asdict())

        cursor.close()
        return data
    
    def get(self,param):
        """
            {
                'nationalite_id':int
            }
        """
        cursor = self.instance.cursor()
        query = "select * from Nationalites where nationalite_id == :nationalite_id;"
        data = None
        for l in cursor.execute(text(query),param):
            data = l._asdict()

        cursor.close()
        return data

class Clientsdb():
    def __init__(self, instance:database,first=False):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """create table if not exists Clients (
                client_id integer primary key {},
                noms char(32) not null,
                addr char(32),
                telephone integer(15) ,
                email char(24),
                nationalite char(24))
                """.format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.commit()
            cursor.close()

    def add(self,param:dict):
        """
            {
                'noms':str,
                'addr':str,
                'telephone':str,
                'mail':str,
                'nationalite':str
            }
        """
        cursor = self.instance.cursor()
        if 'client_id' in  param.keys():
            query = """insert into Clients(client_id, telephone) values(:client_id, :client_id)"""

        else:
            query = "insert into Clients(noms, addr, telephone, email, nationalite) values(:noms, :addr, :telephone, :email, :nationalite);"
        
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def change(self,param):
        """
            {   
                'client_id':int,
                'noms':str,
                'addr':str,
                'telephone':str,
                'mail':str,
                'nationalite_id':str
            }
        """
        cursor = self.instance.cursor()
        query = "update Clients set noms = :noms, addr = :addr, telephone = :telephone, email = :email, nationalite_id = :natiionalite_id where client_id == :client_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def delete(self,param):
        """
            {
                'client_id':int
            }
        """
        cursor = self.instance.cursor()
        query = "delete Cleints where client_id == :client_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def all(self,param=None):
        cursor = self.instance.cursor()
        query = text("select * from Clients;")
        data = {}
        for i in cursor.execute(query):
            d = i._asdict()
            data.update({d.get('client_id'):d})

        cursor.close()
        return data

    def get(self,param):

        cursor = self.instance.cursor()
        query = "select * from Clients where client_id == :client_id;"
        data = None
        for i in cursor.execute(text(query),param):
            data = i._asdict()

        cursor.close()
        return data

class Categoriesdb():
    def __init__(self,instance:database,first=False):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """create table if not exists Categories(
                categorie_id integer primary key {},
                label char(24) not null unique,
                description Text
                )""".format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.close()
        
    def add(self,param):
        """
            {
                'label':str
            }
        """
        cursor = self.instance.cursor()
        query = "insert into Categories(label,description) values (:label,:description);"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()
        
    def change(self,param):
        """
        {
            'categorie_id':int,
            'label':text
        }
        """
        cursor = self.instance.cursor()
        query = "alter Categories set label = :label , description = :description where categorie_id == :categorie_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def delete(self,param):
        """
            {
                'categorie_id':int
            }
        """
        cursor= self.instance.cursor()
        query = "delete Categories where categorie_id == :categorie_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def get(self,param):
        cursor = self.instance.cursor()
        query = "select * from Categories where categorie_id == :categorie_id;"
        data = None
        for l in cursor.execute(text(query),param):
            data = l._asdict()

        cursor.close()
        return data

    def all(self,param=None):
        cursor = self.instance.cursor()
        query = text("select * from Categories;")
        data = []
        for l in cursor.execute(query):
            data.append(l._asdict())

        cursor.close()
        return data

class Ventesdb():
    def __init__(self,instance:database,first=False):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """create table if not exists Ventes(
                vente_id integer primary key {} ,
                client_id integer not null ,
                login_id integer not null,
                marchandises Text ,
                prix Integer, 
                date datetime,
                foreign key (client_id) references Clients(client_id),
                foreign key (login_id) references  Agents(login_id) );
             """.format(instance.autoincrement)
            cursor.execute(text(query)) 
            cursor.close()

    def add(self,data):
        """
            {
                "login_id":int, backend
                "client_id":int,
                "marchandises":dict,
                "prix":int backend,
                "date":date backend
            }
        """
        cursor = self.instance.cursor()
        marchandises = data['marchandises']
        if type(marchandises) != type({}):
            raise TypeEntreException('marchandises')
        
        data['marchandises'] = ''
        price = 0

        for march, quantite in marchandises.items(): 
            info = Produitsdb(self.instance).get({'produit_id':march})
            if not info:
                raise Exception("Ce produit n'existe pas")
            
            q = int(quantite)
            price += (info['prix'] * q)
            print(price)
            data['marchandises']+= f"{info['label']}({q}) "
            
            if q > info['quantite']:
                raise StockInsuffisantException(info['label'])
        
        data['prix'] = price
        data['date'] = get_timestamp()
        data['marchandises'] = data['marchandises'].strip()
        
        if not Clientsdb(self.instance).get(data):
            Clientsdb(self.instance).add(data)

        # nous realisons l achant
        cursor.execute(text("insert into Ventes (client_id,login_id,marchandises,prix,date) values (:client_id,:login_id,:marchandises,:prix,:date)"),data)
        
        for march , quant in marchandises.items():  # nous retranchons les produits vendus du stock
            query = """update Produits set quantite = quantite - :quantite where produit_id == :produit_id"""
            cursor.execute(text(query),{'quantite':quant,'produit_id':march})

        cursor.commit()
        cursor.close()

    def get(self,param):
        """
        {
            'vente_id':int
        }
        """
        """renvoi l element vente"""
        cursor = self.instance.cursor()
        l = None
        for i in cursor.execute(text("select * from Ventes where vente_id == :vente_id;"),param):
            l = i._asdict()
        cursor.close()
        return l

    def all(self,param=None): 
        """ renvoi les elements de la tables ventes """
        cursor = self.instance.cursor()
        ventes = []
        
        if not param:
            param.update({'today':time.strftime("%Y-%m-%d")})
            req = text("select * from Ventes where date(date) == date(:today)")
        else:
            req = text("select * from Ventes where date(date) between date(:from) and date(:to);")

        for i in cursor.execute(req,param):
            ventes.append(i._asdict())
        cursor.close()
        return ventes
    
    def delete(self,param):
        """
        {
            'vente_id':int
        }
        """
        # il faut implimenter le log
        cursor = self.instance.cursor()
        cursor.execute(text('drop from Ventes where vente_id == :vente_id'),param)
        cursor.commit()
        cursor.close()

    def change(self,param): 
        raise MessagePersonnalise("N est pas implemmentee")

class Produitsdb():
    def __init__(self,instance:database,first=False):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """create table if not exists Produits(
                produit_id integer primary key {},
                label char(24) not null unique,
                categorie_id integer not null,
                prix integer unsigned not null,
                photo blob,
                quantite integer unsigned default 0, 
                description Text,
                code_barre integer unique,
                foreign key (categorie_id) references Categories(categorie_id))
            """.format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.commit()
            cursor.close()

    def add(self,param):
        """
            {
                'label':str,
                'categorie_id':int,
                'prix':int,
                'photo':str,
                'description':text
                'code_barre':int
            }
        """
        cursor = self.instance.cursor()
        query = "insert into Produits (label,categorie_id,prix,photo,description,code_barre) values(:label,:categorie_id,:prix,:photo,:description,:code_barre);"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def change(self,param):
        """
            {
                'produit_id':int
                'label':str,
                'categorie_id':int,
                'prix':int,
                'photo':str,
                'description':text
                'code_barre':int
            }
        """
        cursor = self.instance.cursor()
        query = "update Produits set label = :label, categorie_id = :categorie_id, prix = :prix, photo = :photo,description = :description,code_barre = :code_barre where produit_id == :produit_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def delete(self,param):
        cursor= self.instance.cursor()
        query = "delte from Produits where produit_id == :produit_id;"
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def get(self,param):
        cursor = self.instance.cursor()
        query = "select * from Produits where produit_id == :produit_id;"
        data = None
        for i in cursor.execute(text(query),param):
            data = i._asdict()
        return data

    def all(self,param=None):
        cursor = self.instance.cursor()
        query = "select * from Produits;"
        data = []
        for i in cursor.execute(text(query)):
            data.append(i._asdict())

        cursor.close()
        return data

class Arrivagesdb:
    def __init__(self,instance:database,first=False):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """
            create table if not exists arrivages(
                arrivage_id integer primary key {},
                produit_id integer, 
                date datetime, 
                quantite integer,
                foreign key (produit_id) references Produits(produit_id));""".format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.commit()
            cursor.close()

    def add(self,param):
        """
        {
            'produit_id':int,
            'quantite': int
            'date':date auto
        }
        """
        param['date'] = get_timestamp()
        cursor = self.instance.cursor()
        query = """insert into Arrivages (produit_id,date,quantite) values (:produit_id,:date,:quantite)"""
        cursor.execute(text(query),param)
        query = """update Produits set quantite = quantite + :quantite where produit_id == :produit_id"""
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def all(self,param=None):
        cursor = self.instance.cursor()
        query = """select * from Arrivages"""
        data = []
        for i in cursor.execute(text(query)):
            data.append(i._asdict())

        cursor.close()
        return data

    def get(self,param):
        """
        {
            "arrivage_id":int
        }
        """
        cursor = self.instance.cursor()
        query = """select * from arrivages where arrivage_id == :arrivage_id"""
        data = None
        for i in cursor.execute(text(query),param):
            data = i._asdict()

        cursor.close()
        return data

    def delete(self,param):
        """
        {
            'arrivage_id':int
        }
        """
        cursor = self.instance.cursor()
        query = """delete from Arrivages where arrivage_id == :arrivage_id """
        cursor.execute(text(query),param)
        cursor.commit()
        cursor.close()

    def change(self,param): # il ne doit pas existe
        raise MessagePersonnalise('Cette fonctionnalite n est pas implementer ')

