from sqlalchemy import create_engine, text
from .utils import *
from . import my_objects
import time

class database:
    def __init__(self,settings={}):
        self.db = None
        self.settings = settings

    def check(self,db=None):
        net = self.settings.get('connection_type','local')
        db_name =  self.settings.get('db_name') if not db else db

        try:
            if net == 'local':
                db = Path(run_path())
                db.joinpath(db_name)
                conn = create_engine("sqlite:///{}".format(db))
            else:
                user = self.settings.get('db_username')
                passwd = self.settings.get('db_password')
                host = self.settings.get('host')
                conn = create_engine("""
                    mysql+mysqlconnector://{}:{}@{}
                        """.format(user,passwd,host,db_name))
            conn.connect()
        except : 
            pass
        else:
            conn.close()
            return True    

    def connect(self,db=None):
        net = self.settings.get('connection_type','local')
        db_name =  db
        setting_db = self.settings.get('db_name')
        if not db_name:
            if not setting_db:
                db_name = 'settings.db'
            else:
                db_name= setting_db
        if net == 'local':
            db = Path(run_path()).joinpath(db_name)
            self.autoincrement = 'autoincrement'
            conn = create_engine("sqlite:///{}".format(db))
        elif net == 'distant':
            self.autoincrement = 'auto_increment'
            user = self.settings.get('db_username')
            passwd = self.settings.get('db_password')
            host = self.settings.get('host')
            conn = create_engine("""
                mysql+mysqlconnector://{}:{}@{}
                    """.format(user,passwd,host,db_name))
        else:
            raise Exception('Un probleme avec le mode de connection de la db')
        
        self.db = conn
        
    def cursor(self):
        """retourne le cursor"""
        return self.db.connect()

class Settingsdb:
    def __init__(self,instance:database,first=False,config={}):
        self.instance = instance
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists Settings(
                    label char(24) primary key ,
                    value Text
                )"""
                cursor.execute(text(query))
                cursor.commit()

    def add(self,param):
        with self.instance.cursor() as cursor:
            query = """
                insert into Settings(label,value) 
                values(:label,:value)
                """
            cursor.execute(text(query),param)
            cursor.commit()

    def get(self,param):
        data = {}
        with self.instance.cursor() as cursor :
            query = """select value from Settings where label == :label"""
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

        return data
    
    def all(self,param={}):
        data = {}
        with self.instance.cursor() as cursor:
            query = "select * from Settings "
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                data.update({d.get('label'):d.get('value')})
        
        return data

    def change(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = "update Settings set value = :value where label = :label returning *"
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())
            cursor.commit()
        return data

    def delete(self,param):
        with self.instance.cursor() as cursor:
            query = "delete from Settings where label == :label"
            cursor.execute(text(query),param)        

    def save(self):
        """  Enregistre les paramtres dans la db pour une restoration  """
        raise NotImplemented

class Logsdb():
    def __init__(self,instance:database,first=False,config={}):
        self.instance = instance
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists Logs(
                    log_id integer primary key {},
                    date datetime,
                    message varchar(64),
                    action varchar(16),
                    ip_addr  varchar(19)    
                )""".format(instance.autoincrement)
                cursor.execute(text(query))
                cursor.commit()
            #cursor.close()

    def add(self,param):
        """ajout d'un nouveau log"""
        with self.instance.cursor() as cursor:
            query = """
                insert into Logs(date,message,action,ip_addr) 
                values(:date,:message,:action,:ip_addr)
                """
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def get(self,param):
        data = {}
        with self.instance.cursor() as cursor :
            query = """select * from Logs where log_id == :log_id"""
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

        #cursor.close()
        return data
    
    def all(self,param):
        """ j dois mettre en place un filtre mais  """
        data = {}

        with self.instance.cursor() as cursor:
            if param.get('isreport'):
                param['from'] = to_date(param.get('from'))
                param['to'] = to_date(param.get('to'))
                query = "select * from Logs where date between date(:from) and date(:to)"
            else:
                query = """
                    select * from Logs where date(date) == date(:date)
                    """ 
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                data[d.get('log_id')] = d
        
        #cursor.close()
        return data

class Loginsdb():
    def __init__(self,instance:database,config={},first=False):
        self.instance = instance
        self.config = config
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists Logins(
                    login_id integer primary key {},
                    username char(32) unique not null,
                    password char(64) not null,
                    role char(8) not null,
                    statut integer(1) not null default 1)
                """.format(instance.autoincrement)
                cursor.execute(text(query))
                cursor.commit()

            try: # pour fuire lexception sur la contraite d'unitarité
                p = {'username':'MyShop','password':'MyShop','role':'admin'}
                self.add(p)
            except :
                pass

    def check(self,param):
        salt = self.config.get('salt')
        idt = {}
        param['password'] = sha256(bytes(salt+param['password'],'utf-8')).hexdigest()

        with self.instance.cursor() as cursor:
            query = """
                select login_id,statut from Logins where username == :username and password == :password
                """
        
            for i in cursor.execute(text(query),param):
                idt = i._asdict()

            cursor.close()

        if idt:
            if idt['statut'] == 0:
                raise UtilisateurBloquerException(param.get('username'))
        return idt
    
    def reset_passwd(self,param):
        salt = self.config.get('salt')
        if not param.get('password','invalid1') == param.get('confirm_password','invalid'):
            raise MessagePersonnalise('les mots de passes doivent etre identiques')
        
        param['password'] = sha256(bytes(salt+param['password'],'utf-8')).hexdigest()
        param['confirm_password'] = sha256(bytes(salt+param['confirm_password'],'utf-8')).hexdigest()

        with self.instance.cursor() as cursor:
            query = """
                update Logins set password == :password where login_id == :login_id
                """
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def add(self,param:dict):
        salt = self.config.get('salt')
        data = {}
        param['password'] = bytes(salt+param['password'],'utf-8')
        param['password'] = sha256(param['password']).hexdigest()
        with self.instance.cursor() as cursor:
            query = """
                insert into Logins(username,password,role) 
                values(:username,:password,:role) returning login_id,username,role,statut
                """
        
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

            cursor.commit()
        #cursor.close()
        return data

    def change(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                update Logins set role = :role where login_id == :login_id 
                returning login_id, username, role;
                """
        
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

            cursor.commit()
        #cursor.close()
        return data
    
    def delete(self,param):
        with self.instance.cursor() as cursor :
            query = "delete from Logins where login_id == :login_id;"
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()
    
    def all(self,param=None):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                select Logins.login_id as login_id ,username, role, statut from Logins join 
                Agents where logins.login_id == Agents.login_id
                """
        
            for i in cursor.execute(text(query)):
                d = i._asdict()
                data[d.get('login_id')] = d

        #cursor.close()
        return data
    
    def get(self,param):
        res = {}
        with self.instance.cursor() as cursor:
            query = """
                select Logins.login_id as login_id ,username, role, statut from Logins join 
                Agents where logins.login_id == Agents.login_id and Agents.login_id == :login_id
            """
        
            for i in cursor.execute(text(query),param):
                res.update(i._asdict())

        #cursor.close()
        return res

class Sessionsdb():
    def __init__(self,instance:database,first=False,config={}):
        self.db_instance = instance
        if first:
            with self.db_instance.cursor() as cursor:
                query ="""
                    create table if not exists Sessions(
                    session_id integer primary key {},
                    cookies varchar(64) unique not null,
                    statut int unsigned default 1,
                    login_id integer not null,
                    ip_addr varchar(16),
                    date datetime,
                    foreign key (login_id) references Logins(login_id) )
                    """.format(instance.autoincrement)
                cursor.execute(text(query))
                cursor.commit()
            #cursor.close()

    def add(self,param):
        param['cookies'] = get_cookie()
        with self.db_instance.cursor() as cursor:
            query = """
                insert into Sessions(cookies,login_id,ip_addr,date) 
                values(:cookies,:login_id,:ip_addr,:date);
                """
            cursor.execute(text(query),param)
            cursor.commit()
        info = {}
        info.update({'cookie':{'cookie':param['cookies']}})
        need = ['logo','description','boutique','contact']
        for i in need:
            value = self.db_instance.settings.get(i)
            info.update({i:value})
        
        return info
    
    def all(self,param={}):
        data = {}
        with self.db_instance.cursor() as cursor:
            query = """
                select session_id,date,Sessions.statut as statut,username,ip_addr from Sessions 
                join Logins where Sessions.login_id == Logins.login_id """
            if param.get('isreport'):
                param['from'] = to_date(param.get('from'))
                param['to'] = to_date(param.get('to'))
                query += "and date between date(:from) and date(:to)"
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                data[d.get('session_id')] = d

        #cursor.close()
        return data
    
    def delete(self,param):
        with self.db_instance.cursor() as cursor:
            query = """
                delete from Sessions where session_id == :session_id
                """
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def change(self,param): # ou encore bloquer
        with self.db_instance.cursor() as cursor:
            query = """
                update Sessions set statut = 0 where session_id == :session_id return session_id,statut
                """
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def check(self,cookie:dict):
        user_id = {}
        with self.db_instance.cursor() as cursor:
            query = "select login_id from Sessions where cookies == :cookie"
        
            for i in cursor.execute(text(query),cookie):
                user_id.update(i._asdict())

        #cursor.close()
        return user_id

class Agentsdb():
    def __init__(self, instance:database,first=False,config={}):
        self.instance = instance
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists Agents(
                    login_id integer primary key {},
                    noms char(32) not null,
                    addr char(32) ,
                    telephone integer(15),
                    email char(32),
                    photo Text ,
                    foreign key (login_id) references Logins(login_id))
                    """.format(instance.autoincrement)
                cursor.execute(text(query))
                cursor.commit()
            
                try:
                    p = {'addr':'','noms':'noms par defaut','telephone':'','email':'','photo':'','login_id':1}
                    self.add(p)
                except :
                    pass

    def add(self,param):
        data  = {}
        with self.instance.cursor() as cursor:
            query = """
                insert into Agents(noms, addr, login_id, telephone, email,photo) 
                values(:noms,:addr,:login_id,:telephone,:email,:photo) returning *
                """
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

            cursor.commit()
        #cursor.close()
        return data

    def delete(self,param):
        with self.instance.cursor() as cursor:
            query = """
                delete from Agents where login_id == :login_id
            """
            cursor.execute(text(query),param)
            cursor.commit()
        Loginsdb(self.instance).delete(param)
        #cursor.close()

    def change(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                update Agents set noms = :noms, addr = :addr, telephone = :telephone, email = :email,
                photo = :photo where login_id == :login_id returning *
                """
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())
            
            cursor.commit()
        #cursor.close()
        return data

    def all(self,param={}):
        data = {}
        with self.instance.cursor() as cursor:
            query = "select * from Agents"
            for i in cursor.execute(text(query)):
                d = i._asdict()
                data[d.get('login_id')] = d

        #cursor.close()
        return data
    
    def get(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                select * from Agents where login_id == :login_id
                """
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

        #cursor.close()
        return data

class Clientsdb(): 
    def __init__(self, instance:database,first=False,config={}):
        self.instance = instance
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists Clients (
                    client_id integer primary key {},
                    refer_client int default 0,
                    point int default 0,
                    type char(1) default 'D',
                    noms char(32) not null,
                    telephone integer(15) default 0000000000 ,
                    addr char(32) default '',
                    sexe char(12) default '',
                    email char(24) default '',
                    derniere_activite datetime
                    )""".format(instance.autoincrement)
                cursor.execute(text(query))
                cursor.commit()
            #cursor.close()

    def add(self,param:dict):
        data = {}
        if not param.get('isform'):
            query = """
                insert into Clients(client_id,telephone,point,noms,derniere_activite) 
                values(:client_id, :client_id,10,"aucun nom",:date) returning * 
                """

        else:
            if param.get('telephone') and param.get('telephone') != '':
                query = f"""
                    insert into Clients(client_id,noms, addr,sexe ,type, refer_client ,telephone , email, derniere_activite)
                    values(:client_id,:noms, :addr, :sexe, :type, :refer_client ,:telephone ,:email,:date) returning * 
                """
            else:
                query = f"""
                    insert into Clients(noms, addr,sexe ,type, refer_client , email, derniere_activite)
                    values(:noms, :addr, :sexe, :type, :refer_client ,:email,:date) returning * 
                """
        
        with self.instance.cursor() as cursor:
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

            cursor.commit()
        #cursor.close()
        return data

    def change(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                update Clients set noms = :noms, addr = :addr,type = :type, 
                telephone = :telephone, email = :email, sexe = :sexe, point = :point , 
                derniere_activite = :date where client_id == :client_id returning *
                """
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

            cursor.commit()
        #cursor.close()
        return data

    def delete(self,param):
        with self.instance.cursor() as cursor:
            query = "delete from Clients where client_id == :client_id;"
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def all(self,param={}):
        param.update(my_objects.Client(param).map())
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                select * from Clients where (client_id like :client_id) and (refer_client like :refer_client)
                and (noms like :noms) and (addr like :addr) and (type like :type) and (telephone like :telephone)
                and (refer_client like :refer_client) 
                """
            if param.get('isreport'):
                query += " and derniere_activite between date(:from) and date(:to)"
            else:
                query += " order by derniere_activite limit 100"
                
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                data[d.get('client_id')] = d

        #cursor.close()
        return data

    def get(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = "select * from Clients where client_id == :client_id;"
        
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

        #cursor.close()
        return data

class Categoriesdb():
    def __init__(self,instance:database,first=False,config={}):
        self.instance = instance
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists Categories(
                    categorie_id integer primary key {},
                    label char(24) not null unique,
                    description Text
                    )""".format(instance.autoincrement)
                cursor.execute(text(query))
            #cursor.close()
        
    def add(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                insert into Categories(label,description) values (:label,:description) returning *
                """
        
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

            cursor.commit()
        #cursor.close()
        return data
        
    def change(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                alter Categories set label = :label , description = :description where categorie_id == :categorie_id 
                returning *
                """
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())
            cursor.commit()
        #cursor.close()
        return data

    def delete(self,param):
        with self.instance.cursor() as cursor:
            query = "delete Categories where categorie_id == :categorie_id;"
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def get(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = "select * from Categories where categorie_id == :categorie_id;"  
            for l in cursor.execute(text(query),param):
                data.update(l._asdict())

        #cursor.close()
        return data

    def all(self,param={}):
        data = {}
        with self.instance.cursor() as cursor:
            query = "select * from Categories;"
        
            for l in cursor.execute(text(query),param):
                d = l._asdict()
                data[d.get('categorie_id')] = d

        #cursor.close()
        return data

class Ventesdb():
    def __init__(self,instance:database,first=False,config={}):
        self.instance = instance
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists Ventes(
                    vente_id integer primary key {} ,
                    client_id integer not null ,
                    login_id integer not null,
                    marchandises Text ,
                    prix char(128), 
                    date datetime,
                    foreign key (client_id) references Clients(client_id),
                    foreign key (login_id) references  Agents(login_id));
                    """.format(instance.autoincrement)
                cursor.execute(text(query)) 
            #cursor.close()

    def add(self,data):
        marchandises = data['marchandises']
        
        data['marchandises'] = {}
        promotions = Promotionsdb(self.instance).valide(data)
        price = {}

        for march, quantite in marchandises.items():
            info = Produitsdb(self.instance).get({'produit_id':march})
            if not info:
                raise Exception("Ce produit n'existe pas")
            
            q = int(quantite)
            data['produit_id'] = march
            prixi, devise = info.get('prix').split(sep=' ')
            prix = int(prixi)

            for i, d in promotions.items():
                if march in d.get('produits_ids'):
                    prix -= (int(prixi)*d.get('reduction'))//100

            prix = prix * q

            if price.get(devise):
                price[devise] += prix
            else:
                price[devise] = prix

            data['marchandises'].update({info['label']:(q,f"{prix} {devise}")})
            
            if q > info['quantite']:
                raise StockInsuffisantException(info['label'])
            
        data['prix'] = ''

        for dev, pr in price.items():
            data['prix'] += f'+{pr} {dev} '

        data['prix'] = data.get('prix')[1:]

        data['marchandises'] = JSONEncoder().encode(data['marchandises'])
        
        client = Clientsdb(self.instance).get(data)
        if not client:
            client = Clientsdb(self.instance).add(data)
        else:
            if client.get('type') == 'D':
                client['point'] += 10
            else : 
                client['point'] += 15
            client.update({"date":data.get('date')})
            Clientsdb(self.instance).change(client)

        # nous realisons l achant
        query = """
            insert into Ventes (client_id,login_id,marchandises,prix,date) 
             values (:client_id,:login_id,:marchandises,:prix,:date) returning * 
            """
        resp = {}
        with self.instance.cursor() as cursor:
            for i in cursor.execute(text(query),data):
                d = i._asdict()
                d['marchandises'] = JSONDecoder().decode(d.get('marchandises'))
                resp.update(d)
        
            for march , quant in marchandises.items():  # nous retranchons les produits vendus du stock
                query = """
                    update Produits set quantite = quantite - :quantite where produit_id = :produit_id
                    """
                cursor.execute(text(query),{'quantite':quant,'produit_id':march})

            # ajout des point pour chaque client recommander (15 pour le grossist et 10 pour le detail) mais je trouve cest trop lourd 
            r_client = Clientsdb(self.instance).get({'client_id':data.get('refer_client')}) 
            if r_client.get('type') == 'G':
                query = "update Clients set point = point + 15 where client_id == :refer_client"
            else :
                query = "update Clients set point = point + 10 where client_id == :refer_client"
            cursor.execute(text(query),client)
            cursor.commit()

        cursor.commit()
        #cursor.close()
        return resp

    def get(self,param):
        l = {}
        with self.instance.cursor() as cursor:
            query = """
                select vente_id ,client_id ,username , marchandises , prix, date from Ventes 
                join Logins where (Ventes.login_id == Logins.login_id) and (vente_id == :vente_id)
                """
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                d['marchandises'] = JSONDecoder().decode(d.get('marchandises'))
                l.update(d)
            
        #cursor.close()
        return l

    def all(self,param={}): 
        """ renvoi les elements de la tables ventes """
        param.update(my_objects.Vente(param).map())
        ventes = {}
        
        if param.get('isform',False) == False:
            param['today'] = time.strftime("%Y-%m-%d")
            req = """
                select vente_id ,client_id,username as vendeur,marchandises ,prix, date 
                from Ventes join Logins where Ventes.login_id == Logins.login_id and 
                date(date) == date(:today) order by date
                """
        else:
            param['to'] = to_date(param.get('to'))
            param['from'] = to_date(param.get('from'))

            req = """
                select vente_id ,client_id ,username as vendeur,marchandises ,prix, date 
                from Ventes join Logins where (Ventes.login_id == Logins.login_id) and 
                (Ventes.login_id like :login_id) and (client_id like :client_id) and
                (Logins.username like :vendor) and
                date(date) between date(:from) and date(:to) order by date
                """

        with self.instance.cursor() as cursor:
            for i in cursor.execute(text(req),param):
                d = i._asdict()
                d['marchandises'] = JSONDecoder().decode(d.get('marchandises'))
                ventes[d.get('vente_id')] = d

        #cursor.close()
        return ventes
    
    def delete(self,param):
        with self.instance.cursor() as cursor:
            cursor.execute(text('drop from Ventes where vente_id == :vente_id'),param)
            cursor.commit()
        #cursor.close()

    def change(self,param): 
        raise MessagePersonnalise("Cette fonctionnalite n est pas implemmentee")

class Produitsdb():
    def __init__(self,instance:database,first=False,config={}):
        self.instance = instance
        if first:
            cursor = self.instance.cursor()
            query = """create table if not exists Produits(
                produit_id integer primary key {},
                label char(24) not null unique,
                categorie_id integer not null,
                prix char(32),
                quantite integer unsigned default 0, 
                code_barre integer default 000000,
                description Text,
                photo blob,
                foreign key (categorie_id) references Categories(categorie_id))
            """.format(instance.autoincrement)
            cursor.execute(text(query))
            cursor.commit()
            cursor.close()

    def add(self,param):
        data = {}
        prix , devise = sep_prix(param.get('prix'))
        param['prix'] = f'{prix} {devise}'

        with self.instance.cursor() as cursor:
            query = """
                insert into Produits (label,categorie_id,prix,photo,description,code_barre) 
                values(:label,:categorie_id,:prix,:photo,:description,:code_barre) returning *
                """
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

            cursor.commit()
        return data

    def change(self,param):
        data = {}
        prix , devise = sep_prix(param.get('prix'))
        param['prix'] = f'{prix} {devise}'

        with self.instance.cursor() as cursor:
            query = """
                update Produits set label = :label, categorie_id = :categorie_id, prix = :prix, 
                photo = :photo,description = :description,code_barre = :code_barre 
                where produit_id == :produit_id returning *
                """
        
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

            cursor.commit()
        #cursor.close()
        return data

    def delete(self,param):
        with self.instance.cursor() as cursor:
            query = "delete from Produits where produit_id == :produit_id;"
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def get(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                select produit_id,produits.label as label, Categories.label as cat_label, 
                Categories.categorie_id as categorie_id,prix , quantite, code_barre, 
                photo blob, Produits.description as description 
                from Produits join Categories where Produits.categorie_id == Categories.categorie_id and
                produit_id == :produit_id
                """
        
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

        #cursor.close()
        return data

    def all(self,param={}):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                select produit_id,Produits.label as label, Categories.label as cat_label, 
                Categories.categorie_id as categorie_id,prix , quantite, code_barre, 
                Produits.description as description, photo from Produits 
                join Categories where Produits.categorie_id == Categories.categorie_id
                """
            for i in cursor.execute(text(query)):
                d = i._asdict()
                data[d.get('produit_id')] = d

        return data

class Arrivagesdb:
    def __init__(self,instance:database,first=False,config={}):
        self.instance = instance
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists arrivages(
                    arrivage_id integer primary key {},
                    produit_id integer,
                    quantite integer,
                    date datetime, 
                    foreign key (produit_id) references Produits(produit_id))""".format(instance.autoincrement)
                cursor.execute(text(query))
                cursor.commit()

    def add(self,param):
        data = {}
        param['date'] = get_timestamp()
        with self.instance.cursor() as cursor:
            query = """
                insert into Arrivages (produit_id,date,quantite) 
                values (:produit_id,:date,:quantite) returning *
                """
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

            query = """
                update Produits set quantite = quantite + :quantite where produit_id == :produit_id
                """
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()
        return data

    def all(self,param={}):
        param = my_objects.Arrivage(param).map()
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                select arrivage_id , label , Arrivages.quantite as quantite,date from Arrivages 
                join Produits where (label like :label) and Arrivages.produit_id == Produits.produit_id
                """
            if param.get('isreoort'):
                query += " and date between date(:from) and date(:to) "
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                data[d.get('arrivage_id')] = d

        return data

    def get(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                select arrivage_id , label ,quantite ,date 
                from Arrivages join Produits where Arrvages.produit_id == Produits.produit_id 
                and arrivage_id == :arrivage_id
                """
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())

        #cursor.close()
        return data

    def delete(self,param):
        with self.instance.cursor() as cursor:
            query = """
                delete from Arrivages where arrivage_id == :arrivage_id 
                """
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def change(self,param):
        raise MessagePersonnalise('Cette fonctionnalite n est pas implementer ')

class Promotionsdb: 
    def __init__(self,instance:database,first=False,config={}):
        self.instance = instance
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists Promotions(
                    promotion_id integer primary key {},
                    label varchar(64),
                    produits_ids Text,
                    date_depart datetime,
                    date_fin datetime,
                    reduction int(3),
                    description Text)
                    """.format(self.instance.autoincrement)
                cursor.execute(text(query))
                cursor.commit()
            #cursor.close()

    def add(self,param):
        data = {}
        param['produits_ids'] = JSONEncoder().encode(param.get('produits_ids',[]))
        with self.instance.cursor() as cursor:
            query = """
                insert into Promotions(label,produits_ids,date_depart,date_fin,reduction,description) 
                values (:label,:produits_ids,:date_depart,:date_fin,:reduction,:description) returning * 
                """
            for i in cursor.execute(text(query),param):
                d = i._asdict()

                d['produits_ids'] = JSONDecoder().decode(d['produits_ids'])
                ps = []
                for x in d['produits_ids']:
                    p = Produitsdb(self.instance).get({'produit_id':x})
                    if p:
                        ps.append(p.get('label'))

                d['produits_label'] = ps
                data.update(d)
        
            cursor.commit()
        #cursor.close()
        return data

    def delete(self,param):
        with self.instance.cursor() as cursor:
            query = """
                delete from Promotions where promotion_id == :promotion_id
                 """
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def all(self,param={}):
        data = {}
        if param.get('valide',False) == True:
            query = """ 
                select promotion_id, reduction, produits_ids from Promotions 
                 where date(:date) between date(date_depart) and date(date_fin)"""
        else:
            query = "select * from Promotions"
            if param.get('isreport'):
                #query += "  and "
                pass
        with self.instance.cursor() as cursor:
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                d['produits_ids'] = JSONDecoder().decode(d['produits_ids'])
                ps = []
                for x in d['produits_ids']:
                    p = Produitsdb(self.instance).get({'produit_id':x})
                    if p:
                        ps.append(p.get('label'))

                d['produits_label'] = ps
                data[d.get('promotion_id')] = d

        #cursor.close()
        return data
    
    def get(self,param):
        data = {}

        with self.instance.cursor() as cursor:
            query = """
                select * from Promotions where promotion_id == :promotion_id
                """
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                d['produits_ids'] = JSONDecoder().decode(d['produits_ids'])
                ps = []
                for x in d['produits_ids']:
                    p = Produitsdb(self.instance).get({'produit_id':x})
                    if p:
                        ps.append(p.get('label'))

                d['produits_label'] = ps
                data[d.get('promotion_id')] = d
                data.update(d)

        #cursor.close()
        return data
    
    def change(self,param):
        data = {}
        param['produits_ids'] = JSONEncoder().encode(param.get('produits_ids'))
        cursor = self.instance.cursor()
        query = """update Promotions set label = :label, produits_ids = :produits_ids, date_depart = :date_depart, date_fin = :date_fin, reduction = :reducttion , description = :description where promotion_id == :promotion_id """
        for i in cursor.execute(text(query),param):
            data.update(i._asdict())

        cursor.commit()
        cursor.close()
        return data
    
    def valide(self,param): 
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                select promotion_id, reduction, produits_ids from Promotions 
                where date(:date) between date(date_depart) and date(date_fin)
                """
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                d['produits_ids'] = JSONDecoder().decode(d['produits_ids'])
                data[d.get('promotion_id')] = d

        #cursor.close()
        return data

class Notesdb:
    def __init__(self,instance:database,first=False,config={}):
        self.instance = instance
        if first:
            with self.instance.cursor() as cursor:
                query = """
                    create table if not exists Notes(
                    note_id integer primary key {},
                    login_id integer,
                    sujet varchar(64),
                    date datetime,
                    description Text,
                    foreign key (login_id) references Logins(login_id))
                    """.format(self.instance.autoincrement)
                cursor.execute(text(query))
                cursor.commit()
            #cursor.close()

    def add(self,param):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                insert into Notes(login_id,sujet,description,date) 
                values (:login_id,:sujet,:description,:date) returning * 
                """
            for i in cursor.execute(text(query),param):
                data.update(i._asdict())
            cursor.commit()
        #cursor.close()
        return data

    def delete(self,param):
        with self.instance.cursor() as cursor:
            query = """delete from Notes where note_id == :note_id """
            cursor.execute(text(query),param)
            cursor.commit()
        #cursor.close()

    def all(self,param={}):
        data = {}
        with self.instance.cursor() as cursor:
            query = """
                select note_id , username , sujet , date , description from Notes 
                join Logins where Notes.login_id == Logins.login_id
                """
            if param.get('isreport'):
                param['from'] = to_date(param.get('from'))
                param['to'] = to_date(param.get('to'))
                query += " and date betwenn date(:from) and date(:to) "
            for i in cursor.execute(text(query),param):
                d = i._asdict()
                data[d.get('note_id')] = d

        #cursor.close()
        return data
    
    def get(self,param):
        d = {}
        with self.instance.cursor() as cursor:
            query = """
                select note_id , username , sujet , date , description from Notes 
                join Logins where Notes.login_id == Logins.login_id note_id == :note_id
                """
            for i in cursor.execute(text(query),param):
                d.update(i)

        #cursor.close()
        return d
    
    def change(self,param):
        raise MessagePersonnalise('Fonctionnement non implementer')
        data = {}
        cursor = self.instance.cursor()
        query = """update Notes set sujet = :sujet, date = :date, description = :description, login_id = :login_id where note_id == :note_id returning * """

        for i in cursor.execute(text(query),param):
            data.update(i._asdict())

        cursor.commit()
        cursor.close()
        return data

