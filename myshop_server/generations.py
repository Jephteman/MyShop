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

    def get(self,param:dict):
        param_inventaireobj = my_objects.InventaireObject(param)
        param.update({'isreport':True})
        ventes = Ventesdb(self.instance,self.config).all(param_inventaireobj)
        produits = Produitsdb(self.instance,config=self.config).all()
        arrivages = Arrivagesdb(self.instance,config=self.config).all(param)
        inventaire = {}
        initial_info = {'nom_produit':'','identifiant_produit':'','arrivage_recu':0,'quantite_vendu': 0,'quantite_stock':'','prix_vente_initaire':'','prix_vente_total':''}
        for vente_id , vente_info in ventes.items():
            for produit_name, info in vente_info.get('marchandises').items():
                if not produit_name in inventaire.keys():
                    inventaire.update({produit_name:initial_info.copy()})
                    inventaire[produit_name]['nom_produit'] = produit_name
                inventaire[produit_name]['quantite_vendu'] += info[0]
                inventaire[produit_name]['prix_vente_initaire'] = somme_prix(inventaire[produit_name]['prix_vente_initaire'],info[1])
                inventaire[produit_name]['prix_vente_total'] = somme_prix(inventaire[produit_name]['prix_vente_total'],info[2])
        for produit_id , produit_info in produits.items():
            name = produit_info.get('label')
            if  not name in inventaire.keys():
                inventaire.update({name:initial_info.copy()})
                inventaire[name]['nom_produit'] = name
            inventaire[name]['quantite_stock'] = produit_info.get('quantite')
            inventaire[name]['identifiant_produit'] = produit_id
        
        for arrivage_id , arrivage_info in arrivages.items():
            label_produit = arrivage_info.get('label')
            if not label_produit in inventaire.keys():
                inventaire.update({label_produit:initial_info.copy()})
                inventaire[label_produit]['nom_produit'] = label_produit
            inventaire[label_produit]['arrivage_recu'] += int(arrivage_info.get('quantite'))
        return inventaire

