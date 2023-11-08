from tkinter import *
from tkinter import ttk
from functions import *
from fenetre_sec import *
import time 

create_database()

# definition des fonctions 
def list_select(event):
    """selection d'un element dans la liste"""
    item = lc.curselection()
    element = list_vente()[item[0]]
    var_num.set(element[0])
    var_nom.set(element[1])
    var_marchandise.set(element[2])
    var_piece.set(element[3])
    var_type.set(element[4])
    var_date.set(element[5])

def anul_fonc():
    """anulle le entrees utulisateur"""
    var_num.set(get_last_num()+1)
    var_nom.set('')
    var_date.set(time.ctime())
    var_marchandise.set('')
    var_piece.set('1')

def sauv_fonc():
    """rengistre les entrees dans la bd"""
    if num_exist(var_num.get()):
        """ouvre une fenetre pour le lui signalez"""
        f_not_modifie(root)
        return

    if not var_piece.get().isnumeric():
        piece_isnt_integer(root)
        return

    if var_nom.get() == '' or var_marchandise.get() == '' or not (var_marchandise.get() in list_produits()):
        """ouvre n fenetre sec pour lui signalez"""
        remplire_tous(root)
        return
    if int(var_piece.get()) > get_stock(var_marchandise.get()):
        stock_insuffisant(root,var_marchandise)
        return
    
    insert_vente(var_num.get(),var_nom.get(),var_marchandise.get(),var_piece.get(),var_type.get(),var_date.get())
    lc.insert(END,presentation_liste([var_num.get(),var_nom.get(),var_marchandise.get(),var_piece.get(),var_type.get(),var_date.get()]))
    nouv_fonc()
        
def nouv_fonc():
    """reinitialise la valeur des entrees"""
    anul_fonc()
    var_num.set(get_last_num()+1)
    var_date.set(time.ctime())

def arrivage():
    """Ajout des arrivages (marchandises, piece , prix, date)"""

    def insert():
        if piece.get().isnumeric() and produit.get() != "":
            insert_arrivage(produit.get(),prix.get(),piece.get(),time.ctime())
            l_produit.config(values=list_produits())
            f.destroy()
        else:
            Label(f,bg='red',text="Piece doit etre un nombre").grid(row=4,column=0)

    def p_select(even):
        """Selection d'un element dans la list des produits"""
        p = produit.get()
        prix.set(get_prix(p))

    def new_produit():
        def ret():
            """Fonction return"""
            if not (n_produit.get() in var_produits):
                var_produits.append(n_produit.get())
                insert_produit(n_produit.get())
                l_produit.config(values=list_produits())
                l_march.config(values=list_produits())
                n_produit.set('')
                ff.destroy()
            Label(ff,bg='red',text="\"{}\" existe deja".format(n_produit.get())).pack()

        ff = Toplevel(f,width=300,height=300)
        Label(ff,text="Produit ").pack()
        Entry(ff,textvariable=n_produit).pack()
        Button(ff,text="Inserer",command=ret).pack()

    produit = StringVar()
    piece = StringVar()
    prix = StringVar()
    n_produit = StringVar() # nouveau produit

    f = Toplevel(root,width=300,height=300)
    Label(f,text="Produit :").grid(row=0,column=0)
    l_produit = ttk.Combobox(f,values=list_produits(),textvariable=produit)
    l_produit.grid(row=0,column=1)
    l_produit.bind("<<ComboboxSelected>>",p_select)
    Button(f,text="Nouveau",command=new_produit).grid(row=0,column=2)

    Label(f,text="Prix :").grid(row=1,column=0)
    Entry(f,textvariable=prix).grid(row=1,column=1)

    Label(f,text='Pieces :').grid(row=2,column=0)
    Entry(f,textvariable=piece).grid(row=2,column=1)

    Button(f,text="Inserer",command=insert).grid(row=3,column=1) 
    
def inventaire():
    """Ouvre un fenetre secodaire pour faire l'inventaire"""
    pass

def stock():
    """Ouvre la fenetre pour le stock"""
    f_stock(root)


# initialisation des variables
root = Tk() # fenetre princile
root.resizable(height=False,width=False)
# ces variables sont utiliser pour sauvegarder les entrees utilisateur
var_produits = list_produits()

var_num = StringVar() # variable qui contient le nm
var_num.set(get_last_num()+1)
var_nom = StringVar() 
var_date = StringVar()
var_date.set(time.ctime())
var_type = StringVar()
var_type.set('achat')
var_marchandise = StringVar()
var_piece = StringVar()
var_piece.set('1')
menuBar = Menu(root) # ma barred de menu

f_menu = Menu(menuBar,tearoff=0)
menuBar.add_cascade(menu=f_menu,label="Options")

f_menu.add_command(label="Inventaire",command=inventaire)
f_menu.add_command(label="Arrivage",command=arrivage)
f_menu.add_command(label="Stock",command=stock)
f_menu.add_command(label="A propos")
f_menu.add_command(label="Quitter",command=root.destroy)
root.config(menu=menuBar)

Label(root,text="MySHop").pack()

# le frame de droite qui contient la liste 
f1 = Frame(root,bg="blue",width=400,height=300,padx=10,pady=10)

lc = Listbox(f1,height=300,width=100,bg='skyblue')
lc.bind('<Double-Button-1>',list_select)
for i in list_vente():
    lc.insert(END,presentation_liste(i))

sc=Scrollbar(f1,command=lc.yview)
sc.pack(side="right",fill='y')

lc.pack(fill=Y)
f1.pack(side=RIGHT)

lc.configure(yscrollcommand=sc.set)

f2 = Frame(root,bg='blue',width=300,height=200)

Label(f2,text='Num :',border='15',bg='blue').grid(row=0,column=0)
Label(f2,textvariable=var_num).grid(row=0,column=1)

Label(f2,text="Nom :",border='15',bg='blue').grid(row=1,column=0)
Entry(f2,textvariable=var_nom).grid(row=1,column=1)

Label(f2,text="Marchandise :",border='15',bg='blue').grid(row=2,column=0)

#def m_select(even):
#    print(var_marchandise.get())

l_march = ttk.Combobox(f2,values=list_produits(),textvariable=var_marchandise)
l_march.grid(row=2,column=1)
#l_march.bind("<<ComboboxSelect>>",m_select)

Label(f2,text='Piece ',border='15',bg='blue').grid(row=3,column=0)
Entry(f2,textvariable=var_piece).grid(row=3,column=1)

Label(f2,text="gg")

Label(f2,text="Type :",border='15',bg='blue').grid(row=4,column=0)
Radiobutton(f2,text='Achat',value='achat',variable=var_type,bg='blue',state='active').grid(row=4,column=1)
Radiobutton(f2,text='Remise',value='remise',variable=var_type,bg='blue').grid(row=4,column=2)

Label(f2,text="Date :",border='15',bg='blue').grid(row=5,column=0)
Label(f2,textvariable=var_date).grid(row=5,column=1)


Button(f2,text="Nouveau",command=nouv_fonc).grid(row=6,column=0)

Button(f2,text="Annuler",command=anul_fonc).grid(row=6,column=1)

Button(f2,text="Sauvegarder",command=sauv_fonc).grid(row=6,column=2)

f2.pack(side=LEFT,fill=Y)

root.mainloop()