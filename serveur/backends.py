from exceptions import *
from hashlib import sha3_256 as sha256
from database import *
from utils import *

salt = "azertyazerty"
list_db = {
    'Logs':Logsdb,'Logins':Loginsdb,'Sessions':Sessionsdb,'Users':Loginsdb,
    'Nationalites':Nationalitesdb,'Clients':Clientsdb,'Categories':Categoriesdb,
    'Produits':Produitsdb,'Ventes':Ventesdb,'Arrivages':Arrivagesdb,'Agents':Agentsdb
    }

class Users: 
    def __init__(self,instance:database,cookie:dict = {}):
        self.db_instance = instance
        self.cookie = cookie
        if self.cookie:
            self.user = self.is_login()      
            self.user_info = Loginsdb(self.db_instance).get(self.user)

    def all(self,**param):
        if not self.is_login():
            raise NonConnecterException()
        
        if not is_permited(self.user_info['role'],'Users.all'):
            raise PermissionException(f"Vous n'etes pas autoriser à lister sur la ressource users  ")
        
        return Loginsdb(self.db_instance).all(),200
    
    def get(self,param):
        if not self.is_login():
            raise NonConnecterException()
        
        param.update({'login_id':param.get('user_id')})
        if not is_permited(self.user_info['role'],'Users.all'):
            raise PermissionException(f"Vous n'etes pas autorise à voir ses informations")
        
        try:
            return Agentsdb(self.db_instance).get(param),200
        except KeyError as e:
            raise AbsenceParametreException(e)
        
    def add(self,data):
        data.update({'login_id':data.get('user_id')})
        user_list = Loginsdb(self.db_instance).all()
        if data['username'] in user_list:
            raise UserExistException(data['username'])
        
        if user_list:
            if not self.is_login():
                raise NonConnecterException()
            if not is_permited(self.user_info['role'],'Users.add'):
                raise PermissionException(f"Vous ne pouvez pas creer ce compte")

        data['password'] = bytes(salt+data['password'],'utf-8')
        data['password'] = sha256(data['password']).hexdigest()
        data['login_id'] = Loginsdb(self.db_instance).add(data).get('login_id')

        try:
            return Agentsdb(self.db_instance).add(data),200
        except KeyError as e:
            raise AbsenceParametreException(e)

    def delete(self,id):
        if not self.is_login():
            raise NonConnecterException()
          
        id.update({'login_id':id.get('user_id')})
        if not is_permited(self.user_info['role'],'Users.delete'):
            raise PermissionException(f"Vous n'etes pas autorise à supprimer sur cet utilisateur")

        return Agentsdb(self.db_instance).delete(id),200

    def change(self,data):
        if not self.is_login():
            raise NonConnecterException()   

        if not is_permited(self.user_info['role'],'Users.change') and self.user_id != data['login_id']:
            raise PermissionException(f"Vous n'etes pas autoriser a mener cette action")
        
        try:
            Agentsdb(self.db_instance).change(data)
            Loginsdb(self.db_instance).change(data)
            return 'success',200
        except KeyError as e:
            raise AbsenceParametreException(e)
        
    def reset_passwd(self,data):
        if not self.is_login():
            raise NonConnecterException()
        
        if not is_permited(self.user_info['role'],'Users.change') and self.user_id != data['login_id']:
            raise PermissionException(f"Vous n'etes pas autoriser a mener cette action")
        
        try:
            data['password'] = sha256(bytes(salt+data['password'],'utf-8')).hexdigest()
            data['confirm_password'] = sha256(bytes(salt+data['confirm_password'],'utf-8')).hexdigest()

            Loginsdb(self.db_instance).reset_passwd(data)
            return 'success',200
        except KeyError as e:
            raise AbsenceParametreException(e)

    def is_login(self):
        return Sessionsdb(self.db_instance).check(self.cookie)
        
    def login(self,param):
        """
            login into system
            return cookiepasswd
        """
        try:
            param['password'] = sha256(bytes(salt+param['password'],'utf-8')).hexdigest()
            l = Loginsdb(self.db_instance).check(param)
            if l :
                if l['statut'] == 0:
                    raise UtilisateurBloquerException(l['login_id'])
        
                param['login_id'] = l['login_id']
                data = Sessionsdb(self.db_instance).add(param)
                return data,200
            else:
                raise IdentifiantIncorrectException()
        except KeyError as e:
            raise AbsenceParametreException(e)


class ModeleDB :
    namedb = ''
    def __init__(self,db_instance:database,cookie:dict = {}):
        self.db_instance = db_instance
        self.cookie = cookie
        self.user = Users(self.db_instance,cookie = self.cookie)
        if not self.user.is_login() :
            raise NonConnecterException()
        
    def all(self,param=None):
        if not is_permited(self.user.user_info['role'],f'{self.namedb}.all'):
            raise PermissionException(f"Vous ne pouvez pas acceder a la ressource {self.namedb}")
        
        try:
            return list_db[self.namedb](self.db_instance).all(param=param),200
        except KeyError as e:
            raise AbsenceParametreException(e)

    def get(self,param):
        param.update(self.user.user)
        if not is_permited(self.user.user_info['role'],f'{self.namedb}.get'):
            raise PermissionException(f"Vous ne pouvez pas a la resource {self.namedb.lower()}")

        try:
            return list_db[self.namedb](self.db_instance).get(param),200
        except KeyError as e:
            raise AbsenceParametreException(e)

    def change(self,param):
        param.update(self.user.user)
        if not is_permited(self.user.user_info['role'],f'{self.namedb}.change'):
            raise PermissionException(f"vous n'etes pas autorise à modifier la ressource {self.namedb.lower()}")
        try:
            return list_db[self.namedb](self.db_instance).change(param),200
        except KeyError as e:
            raise AbsenceParametreException(e)
        
    def add(self,param):
        param.update(self.user.user)
        if not is_permited(self.user.user_info['role'],f'{self.namedb}.add'):
            raise PermissionException(f"Vous n'etes pas autorise à inserer sur la ressource {self.namedb.lower()}")

        try:
            return list_db[self.namedb](self.db_instance).add(param),200
        except KeyError as e:
            raise AbsenceParametreException(e)

    def delete(self,param):
        param.update(self.user.user)
        if not is_permited(self.user.user_info['role'],f'{self.namedb}.delete'):
            raise PermissionException(f"Vous n'etes pas autorise a supprimer sur la ressource {self.namedb.lower()}")

        try:
            return list_db[self.namedb](self.db_instance).delete(param),200
        except KeyError as e:
            raise AbsenceParametreException(e)

class Ventes(ModeleDB):
    namedb = 'Ventes'

class Categories(ModeleDB):
    namedb = "Categories"

class Produits(ModeleDB):
    namedb = "Produits"

class Logs(ModeleDB):
    namedb = 'Logs'

class Agents(ModeleDB):
    namedb = 'Agents'

class Clients(ModeleDB):
    namedb = 'Clients'

class Nationalites(ModeleDB):
    namedb = 'Nationalites'

class Sessions(ModeleDB):
    namedb = 'Sessions'

class Logins(ModeleDB):
    namedb = 'Logins'

class Arrivages(ModeleDB):
    namedb = 'Arrivages'

def installation(instance:database):
    Logsdb(instance,first=True)
    Loginsdb(instance,first=True)
    Sessionsdb(instance,first=True)
    Agentsdb(instance,first=True)
    # Nationalitesdb(instance,first=True)
    Clientsdb(instance,first=True)
    Categoriesdb(instance,first=True)
    Produitsdb(instance,first=True)
    Ventesdb(instance,first=True)
    Arrivagesdb(instance,first=True)

    def_user = {
        'username':'MyShop','password':'MyShop','role':'admin',
        'addr':'','noms':'noms par defaut','telephone':'','email':'','photo':''
    }
    try:
        Users(instance).add(def_user)
        Nationalitesdb(instance).add({'label':'Imagination'})
    except :
        pass