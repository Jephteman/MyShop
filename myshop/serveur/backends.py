from .exceptions import *
from .database import *
from .utils import *

# regroupe les differentes ressources qui sont disponibles dans le backend
list_db = {
    'Logs':Logsdb,'Logins':Loginsdb,'Sessions':Sessionsdb,'Users':Loginsdb,'Notes':Notesdb,
    'Clients':Clientsdb,'Categories':Categoriesdb,'Promotions':Promotionsdb,#'Settings':Settingsdb,
    'Produits':Produitsdb,'Ventes':Ventesdb,'Arrivages':Arrivagesdb,'Agents':Agentsdb
    }

class Users: 
    def __init__(self,instance:database,cookie:dict = {},config={}):
        self.config = config
        self.db_instance = instance
        self.cookie = cookie
        if self.cookie:
            self.user = self.is_login()
            if self.user:
                self.user_info = Loginsdb(self.db_instance,config=self.config).get(self.user)
            else:
                raise MessagePersonnalise('Veillez vous connecter')

    def all(self,param={}):
        if not self.is_login():
            param['message'] = 'Une tentative de lister les utilisateurs'
            Logsdb(self.db_instance).add(param)
            raise NonConnecterException()
        
        if not is_permited(self.user_info['role'],'Users.all'):
            param['message'] = f"Une tentative de lister les utilisareurs par l'utilisateur {self.user_info.get('username')}"
            Logsdb(self.db_instance).add(param)
            
            raise PermissionException(f"Vous n'etes pas autorisé à lister sur la ressource users  ")
        
        data = Loginsdb(self.db_instance).all()
        param['message'] = f"Acces a la liste des utilisateurs par {self.user_info.get('username')}"
        Logsdb(self.db_instance).add(param)

        return data,200
    
    def get(self,param):
        if not self.is_login():
            param['message'] = 'une tentative de lister les utilisareurs'
            Logsdb(self.db_instance).add(param)
            raise NonConnecterException()
        
        param.update({'login_id':param.get('user_id')})
        if not is_permited(self.user_info['role'],'Users.all'):
            param['message'] = f"une tentative interdite d'access aux infos de l'utiliateur n° {param.get('login_id')}"
            Logsdb(self.db_instance).add(param)
            raise PermissionException(f"Vous n'etes pas autorise à voir ses informations")
        
        try:
            data = Agentsdb(self.db_instance).get(param)
            param['message'] = f"Acces aux infoarmations par {self.user_info.get('username')} de l'utilisateur n° {param.get('login_id')}"
            Logsdb(self.db_instance).add(param)
            return data,200
        except KeyError as e:
            param['message'] = f"requete mal ecrite"
            Logsdb(self.db_instance).add(param)
            raise AbsenceParametreException(e)
        
    def add(self,data):
        data['login_id'] = data.get('user_id')
        
        if not self.is_login():
            data['message'] = f"une tentative interdite de creation d'un utiliateur"
            Logsdb(self.db_instance).add(data)
            raise NonConnecterException()
        if not is_permited(self.user_info.get('role'),'Users.add'):
            data['message'] = f"une tentative de creation d'un compte par {self.user_info.get('username')}"
            Logsdb(self.db_instance).add(data)
            raise PermissionException(f"Vous ne pouvez pas creer ce compte")

        r_login = Loginsdb(self.db_instance,config=self.config).add(data)
        data['login_id'] = r_login.get('login_id')

        try:
            rep = Agentsdb(self.db_instance).add(data)
            data['message'] = f"Creation par {self.user_info.get('username')} l'utilisateur {data.get('username')} "
            Logsdb(self.db_instance).add(data)
        except KeyError as e:
            data['message'] = f"Requete mal ecrite"
            Logsdb(self.db_instance).add(data)
            raise AbsenceParametreException(e)
        else:
            rep.update(r_login)
            return rep,200

    def delete(self,param):
        if not self.is_login():
            param['message'] = f"une tentative interdite de suppression de l'utiliateur"
            Logsdb(self.db_instance).add(param)

            raise NonConnecterException()
          
        param['login_id'] = param.get('user_id')
        if not is_permited(self.user_info['role'],'Users.delete'):
            param['message'] = f"une tentative de suppression par {self.user_info.get('username')} sur l'utiliateur num {param.get('login_id')}"
            Logsdb(self.db_instance).add(param)
            raise PermissionException(f"Vous n'etes pas autorise à supprimer sur cet utilisateur")

        rep = Agentsdb(self.db_instance).delete(param),200
        param['message'] = f"Suppression par {self.user_info.get('username')} de l'utiliateur num {param.get('login_id')}"
        Logsdb(self.db_instance).add(param)
        return rep

    def change(self,data):
        if not self.is_login():
            data['message'] = f"une tentative interdite de changement des informations de l'utilisateur {data.get('login_id')} "
            Logsdb(self.db_instance).add(data)
            
            raise NonConnecterException()   

        if not is_permited(self.user_info['role'],'Users.change') and self.user_id != data['login_id']:

            data['message'] = f"une tentative de modification des informations par {self.user_info.get('username')} de l'utilisateur {data.get('login_id')} "
            Logsdb(self.db_instance).add(data)
            raise PermissionException(f"Vous n'etes pas autoriser a mener cette action")
        
        try:
            Agentsdb(self.db_instance).change(data)
            Loginsdb(self.db_instance,config=self.config).change(data)

            data['message'] = f"une modification ds informations par {self.user_info.get('username')} sur l'utilisateur {data.get('login_id')} "
            Logsdb(self.db_instance).add(data)
            return 'success',200
        except KeyError as e:

            data['message'] = f"une requete mal ecrite de modification d'information"
            Logsdb(self.db_instance).add(data)
            raise AbsenceParametreException(e)
        
    def reset_passwd(self,data):
        if not self.is_login():
            data['message'] = 'une tentative interdite de changer le mdp'
            Logsdb(self.db_instance).add(data)
            raise NonConnecterException()
        
        if not is_permited(self.user_info['role'],'Users.change') and self.user_id != data['login_id']:
            data['message'] = f"une tentative de mdp par l'utilisateur {self.user_info.get('username')} contre l'utilisateur {data.get('login_id')} "
            Logsdb(self.db_instance).add(data)
            raise PermissionException(f"Vous n'etes pas autoriser a mener cette action")
        
        try:

            Loginsdb(self.db_instance).reset_passwd(data)

            data['message'] = f"une modification du mdp par l'utilisateur {self.user_info.get('username')} sur l'utilisateur {data.get('login_id')} "
            Logsdb(self.db_instance).add(data)
            

            return 'success',200
        except KeyError as e:
            raise AbsenceParametreException(e)

    def is_login(self,first:bool=False):
        """
            la methode permet de savoir si le cookie de session est valide
            si first est vrai alors il considere que c'est une tentative pour verifier le cookie 
                quand l'option auto_login est activé côte client
        """
        info = Sessionsdb(self.db_instance).check(self.cookie,first=first)
        return info
        
    def login(self,param):
        try:
            l = Loginsdb(self.db_instance,config=self.config).check(param)
            if l :
                if l.get('statut') == 0:
                    raise UtilisateurBloquerException(l.get('login_id'))
        
                param['login_id'] = l['login_id']
                data = Sessionsdb(self.db_instance).add(param)
                param['message'] = f"Connection de l'utilisateur {param.get('username')}"
                Logsdb(self.db_instance).add(param)
                return data,200
            else:
                param['message'] = f"Echec de connection avec l'utilisateur {param.get('username')}"
                Logsdb(self.db_instance).add(param)
                raise IdentifiantIncorrectException()
        except KeyError as e:
            param['message'] = 'Une requete mal ecrite'
            Logsdb(self.db_instance).add(param)
            raise AbsenceParametreException(e)

class ModeleDB :
    """ Sert de modele de base pour implementer l'authentification et l'autorisation sur les requetes envoyee"""
    namedb = ''
    def __init__(self,instance:database,cookie:dict = {},config={}):
        self.config = config
        self.db_instance = instance
        self.cookie = cookie
        self.user = Users(instance,cookie = self.cookie, config=config)
        if not self.user.is_login() : # nous verifions si l'utilisateur est cnnecter
            raise NonConnecterException()
        
    def all(self,param):
        if not is_permited(self.user.user_info['role'],f'{self.namedb}.all'):
            # l'uilisateur na pas le droit d'effetuer l action
            param['message'] = f"Une tentative interdite de lister sur la resource '{self.namedb}'"
            Logsdb(self.db_instance).add(param)
            raise PermissionException(f"Vous ne pouvez pas acceder a la ressource {self.namedb}")
        
        try:
            data = list_db[self.namedb](self.db_instance).all(param=param) # pour certaines ressources le param est facultatif
            param['message'] = f"Une tentative interdite de suppression de l'utilisateur"
            Logsdb(self.db_instance).add(param)
            return data,200
        except KeyError as e:
            raise AbsenceParametreException(e)

    def get(self,param):
        param.update(self.user.user)
        id_ = f"{self.namedb.lower()[0:-1]}_id"

        if not is_permited(self.user.user_info['role'],f'{self.namedb}.get'):
            param['message'] = f"Une tentative interdite d'access a la ressource '{self.namedb}' numero {param.get(id_)}"
            Logsdb(self.db_instance).add(param)
            raise PermissionException(f"Vous ne pouvez pas a la resource {self.namedb.lower()}")

        try:
            data = list_db[self.namedb](self.db_instance).get(param)
            param['message'] = f"Access a la ressource '{self.namedb}' numero {id_} par l'utilisateur {self.user.user_info.get('username')} "
            Logsdb(self.db_instance).add(param)
            return data,200
        except KeyError as e:
            raise AbsenceParametreException(e)

    def change(self,param):
        param.update(self.user.user)
        id_ = f"{self.namedb.lower()[0:-1]}_id"

        if not is_permited(self.user.user_info['role'],f'{self.namedb}.change'):
            param['message'] = f"une tentative interdite de modification sur la ressource '{self.namedb}' numero {param.get(id_)}"
            Logsdb(self.db_instance).add(param)
            raise PermissionException(f"vous n'etes pas autorise à modifier la ressource {self.namedb.lower()}")
        try:
            data = list_db[self.namedb](self.db_instance).change(param)
            param['message'] = f"Modification de la resource '{self.namedb}' numero {id_} par l'utilisateur {self.user.user_info.get('username')}"
            Logsdb(self.db_instance).add(param)
            return data,200
        except KeyError as e:
            raise AbsenceParametreException(e)
        
    def add(self,param):
        param.update(self.user.user)
        id_ = f"{self.namedb.lower()[0:-1]}_id"
        if not is_permited(self.user.user_info['role'],f'{self.namedb}.add'):
            param['message'] = f"Tentative de creation sur la ressource '{self.namedb}'"
            Logsdb(self.db_instance).add(param)
            raise PermissionException(f"Vous n'etes pas autorise à inserer sur la ressource {self.namedb.lower()}")

        try:
            data = list_db[self.namedb](self.db_instance).add(param)
            param['message'] = f"Ajout d'un element dans la ressource '{self.namedb}' numero {data.get(id_)}  par l'utlisateur {self.user.user_info.get('username')}"
            Logsdb(self.db_instance).add(param)
            return data,200
        except KeyError as e:
            raise AbsenceParametreException(e)

    def delete(self,param):
        param.update(self.user.user)
        id_ = f"{self.namedb.lower()[0:-1]}_id"

        if not is_permited(self.user.user_info['role'],f'{self.namedb}.delete'):
            param['message'] = f"Une tentative interdite de suppression sur la ressource '{self.namedb}' numero {param.get(id_)}"
            Logsdb(self.db_instance).add(param)
            raise PermissionException(f"Vous n'etes pas autorise a supprimer sur la ressource {self.namedb.lower()}")

        try:
            data = list_db[self.namedb](self.db_instance).delete(param)
            param['message'] = f"Suppression de la ressource '{self.namedb}' numero {param.get(id_)} par l'utilisateur {self.user.user_info.get('username')}"
            Logsdb(self.db_instance).add(param)
            return data,200
        except KeyError as e:
            raise AbsenceParametreException(e)

class Ventes(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec vente """    
    namedb = 'Ventes'

class Categories(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec categorie """    
    namedb = "Categories"

class Produits(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec produit """    
    namedb = "Produits"

class Logs(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec Logs """    
    namedb = 'Logs'

class Agents(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec agents """    
    namedb = 'Agents'

class Clients(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec client """    
    namedb = 'Clients'

class Sessions(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec sessions """    
    namedb = 'Sessions'

class Logins(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec logins """    
    namedb = 'Logins'

class Arrivages(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec arrivage """    
    namedb = 'Arrivages'

class Promotions(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec promotions """    
    namedb = 'Promotions'

class Notes(ModeleDB):
    """ Sert de couche d'abstraction pour communiquer avec notes """    
    namedb = 'Notes'

def cleaner(instance:database,config={}):
    """
        S'occupe de faire le netoyage en arriere plan pour supprimmer les sessions invalides et d'autres actions
    """
    while True:
        Sessionsdb(instance=instance).del_expire_cookie()
        
        sleep_time = config.get('back_action_time')
        time.sleep(int(sleep_time))

def initiale_action(instance:database,config={}): # effectue les actions d'initialisation
    logins = Loginsdb(instance,config=config)
    if not logins.all(): # cree le 1er compte sur le serveur
        p = {'username':'MyShop','password':'MyShop','role':'admin'}
        logins.add(p)

    ### d'autres actions

def pass_like(param:dict):
    """
        prepare les données pour etre passer à l'operateur LIKE dans SQL
    """
    for label , value in param.items():
        param.set({label:f"%{value}%"})

    return param


    