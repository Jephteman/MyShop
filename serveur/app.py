from flask import Flask, request
from backends import *
from utils import *

app = Flask(__name__)

host = "localhost"
username = "oem"
passwd = ""
db_name = "mysocialapp"

list_ressource = {
    'logs':Logs,'logins':Logins,'sessions':Sessions,'users':Users,'agents':Agents,
    'nationalites':Nationalites,'clients':Clients,'categories':Categories,
    'produits':Produits,'ventes':Ventes,'arrivages':Arrivages
    }

db_instance = database()
db_instance.connect(host,username,passwd,db_name,net='local')
installation(db_instance)

def error(e:Exception):
    return e.message() if 'message' in dir(e) else SystemException().message()

@app.errorhandler(404)
def page_not_found(err):
    m =  message(("page not found",404))
    return m

@app.route('/api/v1/check')
def check_cookie(): 
    try:
        cookie = request.cookies.to_dict()
        req = Users(db_instance,cookie=cookie).is_login()
        return message(req)
    except Exception as e:
        return error(e)

@app.route('/api/v1/login',methods=['POST'])
def login():
    """
    {
        "username":"",
        "password":""
    }
    """
    data = request.form.to_dict()
    data.update({'ip_addr':request.access_route[0]})
    try:
        res = Users(db_instance).login(data)
        return message(res)
    except Exception as e:
        return error(e)

@app.route('/api/v1/reset_passwd',methods=['POST'])
def reset_passwd():
    param = request.data.decode()
    param = JSONDecoder().decode(param)
    cookie = request.cookies.to_dict()
    try:
        res = Users(db_instance,cookie=cookie).reset_passwd(param)
        return message(res)
    except Exception as e:
        return error(e)

@app.route('/api/v1/<ressource>/add',methods=['POST'])
def add(ressource):
    try:
        param = request.data.decode()
        param = JSONDecoder().decode(param)
        cookie = request.cookies.to_dict()
        req = list_ressource.get(ressource)(db_instance,cookie=cookie).add(param)
        return message(req)
    except ValueError as e:
        print(param)
        return error(e)

@app.route('/api/v1/<ressource>/all',methods=['GET'])
def all(ressource):
    try:
        param = request.args.to_dict()
        cookie = request.cookies.to_dict()
        req = list_ressource.get(ressource)(db_instance,cookie=cookie).all(param=param)
        return message(req)
    except KeyboardInterrupt as e:
        return error(e)
        
@app.route('/api/v1/<ressource>/<id>',methods=['GET'])
@app.route('/api/v1/<ressource>/<id>/get',methods=['GET'])
def get(ressource,id):
    try:
        cookie = request.cookies
        param = {f'{ressource[:-1]}_id':id}
        req = list_ressource.get(ressource)(db_instance,cookie=cookie).get(param)
        return message(req)
    except Exception as e:
        return error(e)

@app.route('/api/v1/<ressource>/change',methods=[ 'POST'])
def change(ressource):
    try:
        param = request.data.decode()
        param = JSONDecoder().decode(param)
        #param.update({f'{ressource[:-1]}_id':id })
        cookie = request.cookies.to_dict()
        req = list_ressource.get(ressource)(db_instance,cookie=cookie).change(param)
        return message(req)
    except Exception as e:
        print(e)
        return error(e)

@app.route('/api/v1/<ressource>/<id>/delete')
def delete(ressource,id):
    try:
        param = {f'{ressource[:-1]}_id':id}
        cookie = request.cookies.to_dict()
        req = list_ressource.get(ressource)(db_instance,cookie=cookie).delete(param)
        return message(req)
    except Exception as e:
        return error(e)


if __name__ == '__main__':
    app.run(debug=True)
