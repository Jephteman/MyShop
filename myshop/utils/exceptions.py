
### utiliser par l'interface graphique
class DeserialException(Exception):
    def __str__(self):
        return 'Les formats des données n\'est pas correcte'
    
class PersonaliseException(Exception):
    def __str__(self):
        return self.args[0]

### Utiliser par le serveur applicatif

class IdentifiantIncorrectException(Exception):
    def message(self):
        text = "Le mot de passe ou le nom d'utilisateur est incorrect"
        return text,302
    
class AbsenceParametreException(Exception):
    def message(self):
        text = f"L'argument '{self.__str__()}' est demande"
        
        return text,302
    
class PermissionException(Exception):
    def message(self):
        text = self.__str__()
        
        return text,302
    
class TypeEntreException(Exception):
    def message(self):
        text = f"'{self.__str__()}' doit etre rempli correctement"
        
        return text,400
    
class UtilisateurBloquerException(Exception):
    def message(self):
        text = f"Le compte '{self.__str__()}' est bloquee"
        
        return text,402
    
class StockInsuffisantException(Exception):
    def message(self):
        text = f"Stock insuffisant pour le produit '{self.__str__()}'"
        
        return text,300
    
class SystemException(Exception):
    def message(self):
        text = "une erreur côté serveur a eu lien"
        
        return text,500

class NonConnecterException(Exception):
    def message(self):
        text = 'Veillez-vous connecter pour effectuer cette action'
            
        return text,403
    
class UserExistException(Exception):
    def message(self):
        text = f"le nom d'utilisateur '{self.__str__()}' est deja utilise "
        return text,400

class EntreeExist(Exception):
    def message(self):
        text = f"'{self.__str__()}' existe deja et ne peux exister en double"
        return text,400
    
class MessagePersonnalise(Exception):
    def message(self):
        text = self.__str__()
        return text,400
    


