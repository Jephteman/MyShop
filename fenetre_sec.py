from tkinter import *
from functions import *

def f_not_modifie(root):
    """Ouvre la fenetre """
    x = Toplevel(root)
    x.geometry('100x100')
    Message(x,bg='skyblue',text="Vous ne pouvez modifié cette objet").pack(side=TOP)
    Button(x,bg='blue',text='OK',command=x.destroy).pack(side=BOTTOM)

def piece_is_integer(root):
    """exige un entier"""
    x = Toplevel(root)
    x.geometry('100x100')
    Message(x,bg='skyblue',text="\"Piece\" doit être un nombre ").pack(side=TOP)
    Button(x,bg='blue',text='OK',command=x.destroy).pack(side=BOTTOM)

def remplire_tous(root):
    x = Toplevel(root)
    x.geometry('100x100')
    Message(x,bg='red',text="Veillez remplire tous les champs correctement").pack(side=TOP)
    Button(x,bg='blue',text='OK',command=x.destroy).pack(side=BOTTOM)


def f_stock(root):
    def list_select(event):
        item = lc.curselection()
        item = list_produits()[item[0]]
        l_march.config(text=item)
        l_prix.config(text=get_prix(item))
        l_nombre.config(text=get_stock(item))
    master = Toplevel(width=720,height=720)
    
    f1 = Frame(master,height=300,width=150)
    Label(f1,text="Marchandises :").grid(row=0,column=0)
    l_march = Label(f1,text="Aucun")
    l_march.grid(row=0,column=1)

    Label(f1,text="Quantités :").grid(row=1,column=0)
    l_nombre = Label(f1,text="Aucun")
    l_nombre.grid(row=1,column=1)

    Label(f1,text="Prix :").grid(row=2,column=0)
    l_prix = Label(f1,text="Aucun")
    l_prix.grid(row=2,column=1)

    f1.pack(side=LEFT)

    f2 = Frame(master,height=300,width=150)

    lc = Listbox(f2,height=300,width=100,bg='skyblue')
    lc.bind('<Double-Button-1>',list_select)

    for i in list_produits():
        lc.insert(END,i)

    sc=Scrollbar(f2,command=lc.yview)
    sc.pack(side="right")#,fill='y')

    lc.pack(fill=Y)

    f2.pack(side=RIGHT)


def stock_insuffisant(root,march):
    f = Toplevel(root,bg='red')
    p = march.get()
    Label(f,text="Le stock du produit {} n'est pas insuffisant".format(p)).pack()
    Label(f,text="Il ne vous reste {} {}".format(get_stock(p),p)).pack()
    Button(f,text='OK',command=f.destroy).pack()
