
class Client:
    def __init__(self,data={}) -> None:
        self.client_id = f"%{data.get('client_id','')}%"
        self.refer_client = f"%{data.get('refer_client','')}%"
        self.point = f"%{data.get('point','')}%"
        self.type = f"%{data.get('type','')}%"
        self.noms = f"%{data.get('noms','')}%"
        self.sexe = f"%{data.get('sexe','')}%"
        self.telephone = f"%{data.get('telephone','')}%"
        self.addr = f"%{data.get('addr','')}%"
        self.email = f"%{data.get('email','')}%"
        self.derniere_activite = f"%{data.get('derniere_activite','')}%"

    def map(self):
        return {
            "client_id":self.client_id,
            'refer_client':self.refer_client,
            'point':self.point,
            'type':self.type,
            'sexe':self.sexe,
            'noms':self.noms,
            'telephone':self.telephone,
            'addr':self.addr,
            'email':self.email,
            'derniere_activite':self.derniere_activite
            }
    
class Vente:
    def __init__(self,data={}) -> None:
        self.vente_id = data.get('vente_id','')
        self.client_id = data.get('client_id','')
        self.login_id = data.get('login_id','')
        self.marchandises = data.get('marchandises','')
        self.prix = data.get('prix','')
        self.date = data.get('date','')
        self.vendor = data.get('vendeur','')

    def map(self):
        return {
            'vente_id':self.vente_id,
            'client_id':f"%{self.client_id}%",
            'login_id':f'%{self.login_id}%',
            'marchandises':self.marchandises,
            'prix':self.prix,
            'date':self.date,
            'vendor':f'%{self.vendor}%'
            }

class Arrivage:
    def __init__(self,data={}) -> None:
        self.arrivage_id = data.get('arrivage_id','')
        self.produit_id = data.get('produit_id','')
        self.quantite = data.get('quantite','')
        self.date = data.get('date','')
        self.label = f"%{data.get('label','')}%"

    def map(self):
        return {
            'arrivage_id':self.arrivage_id,
            'produit_id':self.produit_id,
            'quantite':self.quantite,
            'date':self.date,
            'label':self.label
            }
