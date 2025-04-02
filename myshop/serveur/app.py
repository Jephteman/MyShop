from flask import Flask, request
from .backends import *
from .utils import *
app = Flask(__name__)

list_ressource = {
    'logs':Logs,'sessions':Sessions,'users':Users,'agents':Agents,
    'clients':Clients,'categories':Categories,'notes':Notes,
    'produits':Produits,'ventes':Ventes,'arrivages':Arrivages,'promotions':Promotions
    }

environment = {
    'instance' : None,
    'configurations': {}
}

def error(e:Exception):
    """
        S'occupe d'appeller la methode ^message^ de la classe de l'exception
    """
    return e.message() if 'message' in dir(e) else SystemException().message()

@app.errorhandler(404)
def page_not_found(err):
    """
        Message pour les points de terminaison non prevu, code 444
    """
    m =  message(("page not found",404))
    return m

@app.route('/api/v1/login',methods=['POST'])
def login():
    try:
        data = request.form.to_dict()
        ##param =  serialise(param)
        data['ip_addr'] = request.access_route[0]
        data['action'] = 'connection'
        data['date'] = get_timestamp()

        valide_data(data)
        
        instance = environment.get('instance')
        config = environment.get('configurations')
        res = Users(instance,config=config).login(data)
    except NotImplementedError as e:
        return error(e)
    else:
        return message(res)

@app.route('/api/v1/reset_passwd',methods=['POST'])
def reset_passwd():
    """
        S'occupe de la reinitialisatin du mot de pass d'un qlconque utilisateur
            il attend comme parametre ['username','password','password_confirmation']
    """
    try:
        param = JSONDecoder().decode(param)
        ##param =  serialise(param)
        param['ip_addr'] = request.access_route[0]
        param['action'] = 'modification mdp'
        param['date'] = get_timestamp()

        valide_data(param)

        cookie = request.cookies.to_dict()
        
        instance = environment.get('instance')
        config = environment.get('configurations')
        res = Users(instance,config=config,cookie=cookie).reset_passwd(param)
    except Exception as e:
        return error(e)
    else:
        return message(res)

@app.route('/api/v1/settings/<action>')
def restore_setting(action):
    try:
        param = request.data.decode()
        param = JSONDecoder().decode(param)
        ##param =  serialise(param)
        param['ip_addr'] = request.access_route[0]
        param['action'] = f'{action}'
        param['date'] = get_timestamp()

        valide_data(param)

        cookie = request.cookies.to_dict()
        
        instance = environment.get('instance')
        config = environment.get('configurations')
        req = Settingsdb(instance,config=config,cookie=cookie).do(action)
    except Exception as e:
        return error(e)
    else:
        return message(req)

@app.route('/api/v1/<ressource>/add',methods=['POST'])
def add(ressource):
    """
        S'occupe de faire intermediaire avec le backend
        pour ajouter dans la db mais le client doit etre connecter premierement
            il attend le parametre de type dict
    """
    try:
        param = request.data.decode()
        param = JSONDecoder().decode(param)
        ##param =  serialise(param)
        param['ip_addr'] = request.access_route[0]
        param['action'] = 'ajouter'
        param['date'] = get_timestamp()

        valide_data(param)

        cookie = request.cookies.to_dict()
        
        instance = environment.get('instance')
        config = environment.get('configurations')
        req = list_ressource.get(ressource)(instance,config=config,cookie=cookie).add(param)
    except Exception as e:
        return error(e)
    else:
        return message(req)

@app.route('/api/v1/<ressource>/all',methods=['GET'])
def all(ressource):
    """
        S'occupe de faire intermediaire avec le backend
        pour liser les elements dans la db mais le client doit etre connecter premierement
            il attend le parametre de type dictn (le plus souvent facultatif)
    """
    try:
        param = {}
        data = request.data.decode()
        data = JSONDecoder().decode(data)
        if data:
            param.update(data)
        ##param =  serialise(param)
        param['ip_addr'] = request.access_route[0]
        param['action'] = 'lister'
        param['date'] = get_timestamp()

        valide_data(param)

        cookie = request.cookies.to_dict()
        
        instance = environment.get('instance')
        config = environment.get('configurations')
        req = list_ressource.get(ressource)(instance,config=config,cookie=cookie).all(param=param)
    except KeyboardInterrupt as e:
        return error(e)
    else:
        return message(req)
        
@app.route('/api/v1/<ressource>/<id>',methods=['GET'])
@app.route('/api/v1/<ressource>/<id>/get',methods=['GET'])
def get(ressource,id):
    """
        S'occupe de faire intermediaire avec le backend
        pour acceder a un element dans la db mais le client doit etre connecter premierement
            il attend le parametre de  type entier passé dans l'url
    """
    try:
        cookie = request.cookies
        param = {f'{ressource[:-1]}_id':id}
        ##param =  serialise(param)
        param['action'] = 'recuperer'
        param['date'] = get_timestamp()
        param['ip_addr']  = request.access_route[0]

        valide_data(param)
        
        instance = environment.get('instance')
        config = environment.get('configurations')
        req = list_ressource.get(ressource)(instance,config=config,cookie=cookie).get(param)
    except Exception as e:
        return error(e)
    else:
        return message(req)

@app.route('/api/v1/<ressource>/<id_>/change',methods=[ 'POST'])
def change(ressource,id_):
    """
        S'occupe de faire intermediaire avec le backend
        pour changer un element dans la db mais le client doit etre connecter premierement
            il attend le parametre de type dict
    """
    try:
        param = request.data.decode()
        param = JSONDecoder().decode(param)
        param.update({f'{ressource[:-1]}_id':id_ })
        ##param =  serialise(param)
        param['action'] = 'modification'
        param['date'] = get_timestamp()
        param['ip_addr'] = request.access_route[0]
        
        valide_data(param)

        cookie = request.cookies.to_dict()
        
        instance = environment.get('instance')
        config = environment.get('configurations')
        req = list_ressource.get(ressource)(instance,config=config,cookie=cookie).change(param)
    except InterruptedError as e:
        return error(e)
    else:
        return message(req)

@app.route('/api/v1/<ressource>/<id>/delete')
def delete(ressource,id):
    """
        S'occupe de faire intermediaire avec le backend
        pour supprimer un element dans la db mais le client doit etre connecter premierement
            il attend le parametre de type dict
    """
    try:
        param = {f'{ressource[:-1]}_id':id}
        param['action'] = 'suppression'
        param['date'] = get_timestamp()
        param['ip_addr'] = request.access_route[0]

        valide_data(param)

        cookie = request.cookies.to_dict()
        instance = environment.get('instance')
        config = environment.get('configurations')
        req = list_ressource.get(ressource)(instance,cookie=cookie,config=config).delete(param)
    except Exception as e:
        return error(e)
    else:
        return message(req)

def prepare():
    """
        Prepare le lancement du serveur
    """
    db_settings = database()
    db_settings.connect(db='settings.db')

    db_settings_instance =  Settingsdb(db_settings)

    db_instance = database()
    config = db_settings_instance.all()
    
    if not config:
        #install.run()
        print("Veillez relancer le programme")
        exit()
    
    db_instance.settings.update(config)

    db_instance.connect()

    environment['configurations'] = config
    environment['instance'] = db_instance

def run(arg=None):
    prepare()
    if arg:
        app.run(host=arg.host,port=arg.port)
    else:
        app.run()

if __name__ == '__main__':
    run()