from tkinter import *
from tkinter import ttk
from functions import *
from fenetre_sec import *
import time 
from json import JSONDecoder

creds = is_install()
if creds:
    serialise_creds = JSONDecoder().decode(creds)
    stock_db = Stock(serialise_creds)
    ventes_db = Ventes(serialise_creds)
else:
    setup()
    exit()

# definition des fonctions 
def list_select(event):
    """selection d'un element dans la liste"""
    item = lc.selection()[0]
    element = ventes_db.get_vente(item)
    var_num.set(element[0])
    var_nom.set(element[1])
    var_marchandise.set(element[2])
    var_piece.set(element[3])
    var_type.set(element[4])
    var_date.set(element[5])

    p = stock_db.get_prix(var_marchandise.get())
    f = ret_prix_fourchette(p)
    p = ret_prix_int(p)*int(var_piece.get())
    var_prix.set(str(p)+f)

def anul_fonc():
    """anulle le entrees utulisateur"""
    var_num.set(ventes_db.get_last_num()+1)
    var_nom.set('')
    var_date.set(time.ctime())
    var_marchandise.set('')
    var_piece.set('1')
    var_prix.set('')

def sauv_fonc():
    """rengistre les entrees dans la bd"""
    if ventes_db.num_exist(var_num.get()):
        """ouvre une fenetre pour le lui signalez"""
        var_alert.set("Vous ne pouvez modifiez cette entree")
        return

    if not (var_piece.get().isnumeric() or int(var_piece.get())) > 0:
        var_alert.set("L'entrée piece doit être un nombre superier à 0")
        return

    if var_nom.get() == '' :
        """ouvre n fenetre sec pour lui signalez"""
        var_alert.set("Veillez fournir un nom")
        return
    
    if var_marchandise.get() == '':
        var_alert.set("Le champ Marchandise ne peut pas être null")
        return
    
    if not (var_marchandise.get() in stock_db.list_produits()):
        var_alert.set("Le produit '{}' n'existe pas dans le stock".format(var_marchandise.get()))
        return

    
    if int(var_piece.get()) > stock_db.get_stock(var_marchandise.get()):
        var_alert.set("Le stock pour le produit {} est insuffisant ({} unitès)".format(var_marchandise.get(),stock_db.get_stock(var_marchandise.get())))
        return
    
    ventes_db.insert_vente(var_num.get(),var_nom.get(),var_marchandise.get(),var_piece.get(),var_type.get(),var_date.get())
    lc.insert('','end',iid =var_num.get() ,values = (var_num.get(),var_nom.get(),var_marchandise.get(),var_date.get()))
    nouv_fonc()
        
def nouv_fonc():
    """reinitialise la valeur des entrees"""
    anul_fonc()
    var_num.set(ventes_db.get_last_num()+1)
    var_date.set(time.ctime())

def arrivage():
    """Ajout des arrivages (marchandises, piece , prix, date)"""

    def insert():
        if produit.get().strip() == '':
            alert.set('Le champ produit ne peut pas être null')
            return

        if piece.get().isnumeric() and produit.get().strip() != "":
            stock_db.insert_arrivage(produit.get(),prix.get(),piece.get(),time.ctime())
            l_produit.config(values=stock_db.list_produits())
            f.destroy()
        else:
            alert.set("Piece doit etre un nombre")
            return

    def p_select(even):
        """Selection d'un element dans la list des produits"""
        p = produit.get()
        prix.set(stock_db.get_prix(p))

    def new_produit():
        def ret():
            """Fonction return"""
            if not (n_produit.get().strip() in var_produits):
                if n_produit.get().strip() == "":
                    alert.set('Le champ produit ne peut être null')
                    return
                var_produits.append(n_produit.get().strip())
                stock_db.insert_produit(n_produit.get().strip())
                l_produit.config(values=stock_db.list_produits())
                l_march.config(values=stock_db.list_produits())
                alert.set('Ajouter de {} avec success'.format(n_produit.get()))
                n_produit.set('')
                return 
            
            alert.set("Le produit {} existe déja".format(n_produit.get()))

        ff = Toplevel(f,width=300,height=300,name="arrivage")
        Label(ff,text="Produit ").pack()
        Entry(ff,textvariable=n_produit).pack()
        Button(ff,text="Inserer",command=ret).pack()
        Label(ff,bg='red',textvariable=alert).pack()

    produit = StringVar()
    piece = StringVar()
    prix = StringVar()
    n_produit = StringVar() # nouveau produit
    alert = StringVar()

    f = Toplevel(root,width=300,height=300)
    Label(f,text="Produit :").grid(row=0,column=0)
    l_produit = ttk.Combobox(f,values=stock_db.list_produits(),textvariable=produit)
    l_produit.grid(row=0,column=1)
    l_produit.bind("<<ComboboxSelected>>",p_select)
    Button(f,text="Nouveau",command=new_produit).grid(row=0,column=2)

    Label(f,text="Prix :").grid(row=1,column=0)
    Entry(f,textvariable=prix).grid(row=1,column=1)

    Label(f,text='Pieces :').grid(row=2,column=0)
    Entry(f,textvariable=piece).grid(row=2,column=1)
    Button(f,text="Inserer",command=insert).grid(row=3,column=1)
    Label(f,textvariable=alert).grid(row=4,column=0)
    
def inventaire():
    """Ouvre un fenetre secodaire pour faire l'inventaire"""
    pass

def stock():
    """Ouvre la fenetre pour le stock"""
    master = Toplevel(root,height=100)
    master.resizable(width=False,height=False)

    f1 = Frame(master,width=300)#,height=300,width=150)
    tab = ttk.Treeview(f1,columns=('marchandise','quantite','prix'))#,height=300)
    tab.heading('marchandise',text='Marchandises')
    tab.heading('quantite',text="Quantités")
    tab.heading('prix',text="Prix")
    tab['show']='headings'

    for i in stock_db.get_stock_all():
        tab.insert('','end',values=(i[0],i[2],i[1]))

    sc=Scrollbar(f1,command=tab.yview)
    sc.pack(side="right",fill=Y)

    tab.configure(yscrollcommand=sc.set)

    tab.pack(fill=Y)

    f1.pack(side=RIGHT)

def about():
    f_about(root)

# initialisation des variables
root = Tk(className="Myshop") # fenetre princile
root.resizable(width=False,height=True)

# ces variables sont utiliser pour sauvegarder les entrees utilisateur
var_produits = stock_db.list_produits()
var_num = StringVar() # variable qui contient le nm
var_num.set(ventes_db.get_last_num()+1)
var_nom = StringVar() 
var_date = StringVar()
var_date.set(time.ctime())
var_type = StringVar()
var_type.set('achat')
var_marchandise = StringVar()
var_piece = StringVar()
var_piece.set('1')
var_prix = StringVar()

var_alert = StringVar()

menuBar = Menu(root) # ma barred de menu

f_menu = Menu(menuBar,tearoff=0)
menuBar.add_cascade(menu=f_menu,label="Options")

f_menu.add_command(label="Inventaire",command=inventaire)
f_menu.add_command(label="Arrivage",command=arrivage)
f_menu.add_command(label="Stock",command=stock)
f_menu.add_command(label="A propos",command=about)
f_menu.add_command(label="Quitter",command=root.destroy)
root.config(menu=menuBar,height=500,width=700)

Label(root,text=serialise_creds['name'],background='skyblue').pack(fill='x')

# le frame de droite qui contient la liste 
f1 = Frame(root,bg="blue",width=400,height=300,padx=10,pady=10)

lc = ttk.Treeview(f1,columns=('id','name','produit','date'),height=500)
lc.heading('id',text='ID')
lc.heading('name',text='Nom')
lc.heading('produit',text='Produit')
lc.heading('date',text='Date')
lc['show']='headings'

lc.bind('<Double-Button-1>',list_select)
for i in ventes_db.list_vente():
    lc.insert('','end',iid=i[0],values=(i[0],i[1],i[2],i[5]))

sc=Scrollbar(f1,command=lc.yview)
sc.pack(side="right",fill='y')

lc.pack(fill=Y)
f1.pack(side=RIGHT)

lc.configure(yscrollcommand=sc.set)

f2 = Frame(root,bg='blue')#,width=300,height=200)

Label(f2,text='Num :',border='15',bg='blue').grid(row=0,column=0)
Label(f2,textvariable=var_num).grid(row=0,column=1)

Label(f2,text="Nom :",border='15',bg='blue').grid(row=1,column=0)
Entry(f2,textvariable=var_nom).grid(row=1,column=1)

Label(f2,text="Marchandise :",border='15',bg='blue').grid(row=2,column=0)

l_march = ttk.Combobox(f2,values=stock_db.list_produits(),textvariable=var_marchandise)
l_march.grid(row=2,column=1)

Label(f2,text='Piece ',border='15',bg='blue').grid(row=3,column=0)
Entry(f2,textvariable=var_piece).grid(row=3,column=1)

Label(f2,text="Prix :",border='15',bg='blue').grid(row=4,column=0)
Label(f2,textvariable=var_prix).grid(row=4,column=1)

Label(f2,text="Type :",border='15',bg='blue').grid(row=5,column=0)
Radiobutton(f2,text='Achat',value='achat',variable=var_type,bg='blue',state='active').grid(row=5,column=1)
Radiobutton(f2,text='Remise',value='remise',variable=var_type,bg='blue').grid(row=5,column=2)

Label(f2,text="Date :",border='15',bg='blue').grid(row=6,column=0)
Label(f2,textvariable=var_date).grid(row=6,column=1)

Button(f2,text="Nouveau",command=nouv_fonc).grid(row=7,column=0)

Button(f2,text="Annuler",command=anul_fonc).grid(row=7,column=1)

Button(f2,text="Sauvegarder",command=sauv_fonc).grid(row=7,column=2)

f2.pack()

f0 = Frame(root,height=10,width=100)
Label(f0,textvariable=var_alert,background='red').pack()
f0.pack(side=BOTTOM)

root.mainloop()