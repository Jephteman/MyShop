import sqlite3

# ma db
db = sqlite3.connect('database.db')

def create_database():
    """cree la bd et ses tables"""
    cursor = db.cursor()
    cursor.execute("create table if not exists ventes(num ,nom ,marchandise, piece,type, date)") #utiliser pour l'inventaire et la journalisation
    cursor.execute("create table if not exists stock(marchandise, prix, quantite integer)") # 
    cursor.execute("create table if not exists arrivages(marchandise, prix, quantite integer, date)") # journalise les arrivages
    cursor.close()

def insert_vente(num,nom,marchandise,piece,type_,date):
    """insert les donnees dans la table ventes"""
    cursor = db.cursor()
    cursor.execute("insert into ventes values (?,?,?,?,?,?)",(str(num),nom,marchandise,piece,type_,date))

    if type_ == 'achat':
        cursor.execute("update stock set quantite = quantite - ? where marchandise = ?",(piece,marchandise,))
    else: 
        cursor.execute("update stock set quantite = quantite + ? where marchandise = ?",(piece,marchandise,))
        
    db.commit()
    cursor.close()

def insert_stock(march,prix,n,date): # inachever
    cursor = db.cursor()
    cursor.execute("update stock set prix = ? where marchandise = ?",(prix,march,))
    cursor.execute("update stock set quantite = quatite + ? where marchandise = ?",(n,march,))
    db.commit()
    cursor.close()

def insert_produit(produit):
    """inserer un nouveau produit"""
    cursor = db.cursor()
    cursor.execute("insert into stock values (?,?,?)",(produit,0,0))
    db.commit()
    cursor.close()

def get_prix(march):
    cursor = db.cursor()
    prix = 0
    for p in cursor.execute("select prix from stock where marchandise == (?);",(march,)):
        prix = p[0]
    cursor.close()
    return prix

def get_stock(march):
    """retourne le stock d'une marchandise"""
    cursor = db.cursor()
    n = 0
    for i in cursor.execute("select quantite from stock where marchandise == ?",(march,)):
        n = i[0]
    cursor.close()
    return n

def insert_arrivage(marchandise,prix, quantite,date):
    """insert le sentree dans la tables arrivages"""
    cursor = db.cursor()
    cursor.execute("insert into arrivages values (?,?,?,?)",(marchandise,prix,quantite,date))
    if marchandise in list_produits():
        cursor.execute("update stock set prix = ? where marchandise = ?",(prix,marchandise))
        cursor.execute("update stock set quantite = quantite + ? where marchandise = ?",(quantite,marchandise))
    else:
        cursor.execute("insert into stock values (?,?,?)",(marchandise,prix,quantite))
    db.commit()
    cursor.close()

def get_last_num():
    """renvoi le num du dernier element dans la table ventes"""
    cursor = db.cursor()
    n = 0
    for num in cursor.execute('select num from ventes'):
        n = num
    
    cursor.close()

    try:
        return int(n[0])
    except:
        return n
    
def num_exist(num):
    """verifie si un num existe deja dans la table ventes"""
    cursor = db.cursor()
    j = (0,0)
    for i in cursor.execute("select num from ventes where num = ?",(num)):
        j = i

    if j[0] == 0:
        return False
    return True

def list_vente(): # je pense qu'il faut s'y prendre autrement
    """renvoi les elements de la tables ventes"""
    cursor = db.cursor()
    ventes = []
    for num, nom, marc, piece,type_, date in cursor.execute("select * from ventes"):
        ventes.append([num, nom, marc, piece,type_, date ])
    cursor.close()
    return ventes

def get_vente(i):
    """renvoi l element vente"""
    cursor = db.cursor()
    l = cursor.execute("select * from ventes where num = ?",(i)).fetchall()
    cursor.close()
    return l

def list_produits():
    """listes de produits"""
    cursor = db.cursor()
    l = []
    for i in cursor.execute("select marchandise from stock"):
        l.append(i[0])
    cursor.close()
    return l

def ret_prix_int(p):
    """Return le prix entant que nombre"""
    n = '0'
    for i in p:
        if i.isnumeric():
            n+=i
    return int(n)

def ret_prix_fourchette(p):
    """retourne la fourchette de prix"""
    f = ''
    for i in p:
        if not i.isnumeric():
            f+=i
    return f