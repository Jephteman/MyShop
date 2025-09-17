from .utils import get_timestamp, sep_prix, to_date,MessagePersonnalise

class ModelObject(dict):
    def __init__(self,attributs:list,param:dict={}):
        self.attribut = attributs
        args = {}
        for i in attributs:
            args.update({i:param.get(i,'')})
        if 'date' in attributs and not param.get('date'):
            param['date'] = get_timestamp()

        super().__init__(args)
    
    def to_like(self,excepts=[]):
        values = self.copy()
        temp = {}
        for key , value in values.items():
            if key not in self.attribut: 
                continue
            temp[key] = f"%{value}%"

        values.update(temp)
        return values

class CookieObject(ModelObject):
    """
    Une classe héritant de dict pour représenter une cookie 
    """
    def __init__(self, param):
        super().__init__(
            ['token','user_id'],
            param
        )
    def __repr__(self):
        return f"<Cookie token={self.get('token')}'>"

class NotificatiionObject(ModelObject):
    """
    Une classe héritant de dict pour représenter une notification de la table Notifications.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param):
        super().__init__(
            ['notification_id','message','niveau','date'],
            param
        )
    def __repr__(self):
        return f"<Notification id={self.get('note_id')}'>"

class NoteObject(ModelObject):
    """
    Une classe héritant de dict pour représenter une note de la table Notes.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param):
        super().__init__(
            ['note_id','login_id','sujet','date','description'],
            param
        )
    def __repr__(self):
        return f"<Note id={self.get('note_id')}'>"
    
class PromotionObject(ModelObject):
    """
    Une classe héritant de dict pour représenter une promotion de la table Promotions.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['promotion_id','label','produits_ids',
            'date_depart','date_fin','reduction','description','date'],
            param
        )

    def __repr__(self):
        return f"<Promotion id={self.get('promotion_id')}>"

class ArrivageObject(ModelObject):
    """
    Une classe héritant de dict pour représenter un arrivage de la table arrivages.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['arrivage_id','produit_id','quantite','date'],
            param
        )

    def __repr__(self):
        return f"<Arrivage id={self.get('arrivage_id')} >"

class ProduitObject(ModelObject):
    """
    Une classe héritant de dict pour représenter un produit de la table Produits.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['produit_id','label','categorie_id','prix_achat','prix_vente',
            'quantite','code_barre','description','photo','date_expiration','date_modification'],param
        )
        prix , devise = sep_prix(self.get('prix_achat'))
        self['prix_achat'] = f'{prix} {devise}'

        prix , devise = sep_prix(self.get('prix_vente'))
        self['prix_vente'] = f'{prix} {devise}'

        self['date_modification'] = get_timestamp()

    def __repr__(self):
        return f"<Produit id={self.get('produit_id')}>"

class VenteObject(ModelObject):
    """
    Une classe héritant de dict pour représenter une vente de la table Ventes.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['vente_id','client_id','login_id','marchandises','prix','date','vendor'],param
        )
        if not self.get('client_id'):
            self['client_id'] = 0
        
    def __repr__(self):
        return f"<Vente id={self.get('vente_id')} >"
    
class CategorieObject(ModelObject):
    """
    Une classe héritant de dict pour représenter une catégorie de la table Categories.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['categorie_id','label','description'],param
        )

    def __repr__(self):
        return f"<Categorie id={self.get('categorie_id')} >"

class ClientObject(ModelObject):
    """
    Une classe héritant de dict pour représenter un client de la table Clients.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['client_id','refer_client','point','type','noms','telephone','addr','sexe','email','derniere_activite'],
            param
        )

    def __repr__(self):
        return f"<Client id={self.get('client_id')}>"

class AgentObject(ModelObject):
    """
    Une classe héritant de dict pour représenter un agent de la table Agents.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['login_id','noms','addr','telephone','email','photo'],param
        )

    def __repr__(self):
        return f"<Agent id={self.get('login_id')} >"

class SessionObject(ModelObject):
    """
    Une classe héritant de dict pour représenter une session de la table Sessions.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['session_id','cookies','statut','login_id','ip_addr','date'],param
        )

    def __repr__(self):
        return f"<Session id={self.get('session_id')}>"

class LoginObject(ModelObject):
    """
    Une classe héritant de dict pour représenter un login de la table Logins.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['login_id','username','password','role','statut','date'],param
        )

    def __repr__(self):
        return f"<Login id={self.get('login_id')} >"

class LogObject(ModelObject):
    """
    Une classe héritant de dict pour représenter un log de la table Logs.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['log_id','date','message','action','ip_addr' ],param
        )

    def __repr__(self):
        return f"<Log id={self.get('log_id')} >"

class SettingObject(ModelObject):
    """
    Une classe héritant de dict pour représenter un paramètre de la table Settings.
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['label','value'],param
        )

    def __repr__(self):
        return f"<Setting label='{self.get('label')}>"

class VenteFiltreObject(ModelObject):
    """
    Une classe héritant de dict pour représenter 
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['login_id', 'client_id','vendor','date'],param
        )
        self['to'] = param.get('to','')
        self['from'] = param.get('from','')

        if not self['to']:
            self['to'] = self['date']
        if not self['from']:
            self['from'] = self['date']


    def __repr__(self):
        return f"<VenteFiltreObject >"

class InventaireObject(ModelObject):
    """
    Une classe héritant de dict pour représenter un paramètre de la 
    Permet une sérialisation facile et un accès par attribut.
    """
    def __init__(self, param = {}):
        super().__init__(
            ['login_id', 'client_id','vendor','date'],param
        )

        self['to'] = to_date(param.get('to'))
        self['from'] = to_date(param.get('from'))

        if not self['to']:
            self['to'] = self['date']
        if not self['from']:
            self['from'] = self['date']


    def __repr__(self):
        return f"<InventaireObject >"