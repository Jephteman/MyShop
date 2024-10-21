from json import JSONDecoder , JSONEncoder
from exceptions import *
import requests

_cred = {'cookie':''}

class API():
    def __init__(self,ressource):
        """
                data : un dictionnaire qui contient imperativement
                    * url : str
                    * protocole : str (default http)produit
                    * cookie : str (dict)
        """
        self.base_url = _cred['url']
        self.name = ressource

    def connect(self,data):
        """login to th server """
        url = f"{self.base_url}/api/v1/login"
        req = requests.post(url,data=data)
        if req.status_code == 200:
            _cred['uname'] = data.get('username')
            _cred['cookie'] = JSONDecoder().decode(req.text)['data']
        else:
            raise PersonaliseException(req.text)
    
    def check_cookie(self):
        """verifie si le cookie de session est valide"""
        url = f"{self.base_url}/api/v1/check"
        req = requests.get(url,cookies=_cred['cookie'])
        if req.status_code == 200:
            return True

    def add(self,param):
        param = JSONEncoder().encode(param)
        url = f'{self.base_url}/api/v1/{self.name}/add'
        req = requests.post(url,data=param,cookies=_cred['cookie'])
        if req.status_code == 200:
            return JSONDecoder().decode(req.text)['data']
        raise PersonaliseException(req.text)

    def get(self,id):
        """return un seul element"""
        url = f'{self.base_url}/api/v1/{self.name}/{id}/get'
        req = requests.get(url,cookies=_cred['cookie'])
        if req.status_code == 200:
            data = JSONDecoder().decode(req.text)['data']
            return data
        raise PersonaliseException(req.text)
   
    def all(self,param=None):
        url = f"{self.base_url}/api/v1/{self.name}/all"
        req = requests.get(url,cookies=_cred['cookie'],params=param)
        if req.status_code == 200:
            data = JSONDecoder().decode(req.text)['data']
            return data
        raise PersonaliseException(req.text)
   
    def change(self,param):
        param = JSONEncoder().encode(param)
        url = f"{self.base_url}/api/v1/{self.name}/change"
        req = requests.post(url,cookies=_cred['cookie'],data=param)
        if req.status_code == 200:
            resp= JSONDecoder().decode(req.text)['data']
            return resp
        raise PersonaliseException(req.text)
    
    def delete(self,id):
        url = f"{self.base_url}/api/v1/{self.name}/{id}/delete"
        req = requests.get(url,cookies=_cred['cookie'])
        if req.status_code == 200:
            resp= JSONDecoder().decode(req.text)['data']
            return resp 
        raise PersonaliseException(req.text)

    def reset_passwd(self,param):
        param = JSONEncoder().encode(param)
        url = f"{self.base_url}/api/v1/reset_passwd"
        req = requests.post(url,cookies=_cred['cookie'],data=param)
        if req.status_code == 200:
            resp= JSONDecoder().decode(req.text)['data']
            return resp
        raise PersonaliseException(req.text)
    
    



