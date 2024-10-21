from json import JSONEncoder

class IdentifiantIncorrectException(Exception):
    def message(self):
        text = {
            'code':302,
            'message':"Le mot de passe ou le nom d'utilisateur est incorrect"
        }
        return JSONEncoder().encode(text),302
    
class AbsenceParametreException(Exception):
    def message(self):
        text = {
            'code':302,
            "message":f"L'argument '{self.__str__()}' est demande"
        }
        return JSONEncoder().encode(text),302
    
class PermissionException(Exception):
    def message(self):
        text = {
            'code':302,
            'message':self.__str__()
        }
        return JSONEncoder().encode(text),302
    
class TypeEntreException(Exception):
    def message(self):
        text = {
            'code':302,
            'message':f"{self.__str__()} n'accepte pas ce type de donnée"
        }
        return JSONEncoder().encode(text),400
    
class UtilisateurBloquerException(Exception):
    def message(self):
        text = {
            'code':402,
            'message':f"Le compte '{self.__str__()}' est bloquee"
        }
        return JSONEncoder().encode(text),402
    
class StockInsuffisantException(Exception):
    def message(self):
        text = {
            'code':300,
            'message':f"Stock insuffisant pour le produit '{self.__str__()}'"
        }
        return JSONEncoder().encode(text),300
    
class SystemException(Exception):
    def message(self):
        text = {
            'code':500,
            'message':"une erreur côté serveur a eu lien"
        }
        return JSONEncoder().encode(text),500

class NonConnecterException(Exception):
    def message(self):
        text = {
            'code':403,
            'message':'Veillez-vous connecter pour effectuer cette action'
            }
        return text,403
    
class UserExistException(Exception):
    def message(self):
        text = {
            'code':400,
            'message':f"le nom d'utilisateur '{self.__str__()}' est deja utilise "}
        return text,400

class EntreeExist(Exception):
    def message(self):
        text = {
            'code':400,
            'message':f"'{self.__str__()}' existe deja et ne peux exister en double"}
        return text,400
    
class MessagePersonnalise(Exception):
    def message(self):
        text = {
            'code':400,
            'message':self.__str__()}
        return text,400
    
