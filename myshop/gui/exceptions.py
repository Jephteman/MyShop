from json import JSONDecoder

class DeserialException(Exception):
    def __str__(self):
        return 'Les formats des données n\'est pas correcte'
    
class PersonaliseException(Exception):
    def __str__(self):
        return self.args[0]



