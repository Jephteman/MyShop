from .database import *


class GraphiqueGen:
    def __init__(self,instance:database,config={}):
        self.instance = instance
        self.config = config

    def get(self,param):
        format = param.get('graphe_fonction')
        support_format = [
        'date2n_vente',
        'client2n_vente',
        'produit2n_vente',
        'vendeur2n_vente'
        ]
        if not format in support_format:
            raise MessagePersonnalise("Le format de graphique n'est oas supporté")

        items_vente_dict = {}
        
        for id_ , values in Ventesdb(self.instance,config=self.config).all(param).items():
            if format == 'date2n_vente':
                discriminant = self.model_date(values.get('date'),param.get('date_fonction','day2day'))
            elif format == 'client2n_vente':
                discriminant = values.get('client_id')
            elif format == 'vendeur2n_vente':
                discriminant = values.get('vendeur')
            elif format == 'produit2n_vente':
                discriminant = 'produit_'

            if discriminant != 'produit_':
                if not discriminant in items_vente_dict.keys():
                    items_vente_dict.update({discriminant:0})
                items_vente_dict[discriminant] += 1
                continue

            for p_name, quantite_prix in values.get('marchandises').items():
                if not p_name in items_vente_dict.keys():
                    items_vente_dict.update({p_name:0})
                items_vente_dict[p_name] += quantite_prix[0]

        return items_vente_dict
    
    def model_date(self,date, format): 
        date = date.split(sep=' ')[0]
        support_format = [
            'day2day',
            'month2month'
        ]
        if not format in support_format:
            raise MessagePersonnalise("Le format de date n'est pas pris en charge")

        if format == 'day2day':
            return date
        if format == 'month2month':
            return date[:-3]
        
class InventaireGen:
    def __init__(self,instance:database,config={}):
        self.instance = instance
        self.config = config

    def get(self,param):
        param = my_objects.InventaireObject(param)
        ventes = Ventesdb(self.instance,self.config).all(param)
        produits = Produitsdb(self.instance,config=self.config).all()
        inventaire = {}
        for vente_id , vente_info in ventes.items():
            for produit_name, info in vente_info.get('marchandises'):
                if not produit_name in inventaire.keys():
                    put = {'quantite_vendu': 0,'quatite_stock':'','prix_vente_initaire':'','prix_vente_total':''}
                    inventaire.update({produit_name:put})

                inventaire[produit_name]['quantite_vendu'] += info[0]
                inventaire[produit_name]['prix_vente_initaire'] = somme_prix(inventaire[produit_name]['prix_vente_initaire'],info[1])
                inventaire[produit_name]['prix_vente_total'] = somme_prix(inventaire[produit_name]['prix_vente_total'],info[2])

        for produit_id , produit_info in produits.items():
            name = produit_info.get('label')
            if  name in inventaire.keys():
                inventaire[name]['quantite_stock'] = produit_info.get('quantite')

        return inventaire

