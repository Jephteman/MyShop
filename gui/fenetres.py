import time 
from utils import * 
from admini_windows import *
from tkinter import *
from tkinter import ttk

dict_produits = {}
dict_categries = {}

id_name_produits = {}
id_name_categories = {}

def actualise_prod():
    """actualise la liste de produits maos,najoute pas dans le widget et neffectue aussi le retrait des elements"""

    for m in client.API('produits').all():
        dict_produits.update({m.get('label'):m})
        id_name_produits.update({m.get('produit_id'):m.get('label')})

def actualise_cat():
    """actualise la liste de categorie maos,najoute pas dans le widget et neffectue aussi le retrait des elements"""
    
    for c in client.API('categories').all():
        dict_categries.update({c.get('label'):c})
        id_name_categories.update({c.get('categorie_id'):c.get('label')})

def actualise_all():
    """actualise la liste des produits et aaussi des categories"""
    actualise_cat()
    actualise_prod()


class arrivage():
    def __init__(self):
        """Ajout des arrivages (marchandises, piece , prix, date)"""
        produit = StringVar()
        piece = IntVar()
        self.n_produit = StringVar() # nouveau produit


        def ret():
            pdt = dict_produits.get(produit.get())

            if not produit:
                alert_wn("Veillez choisir un produit qui existe dans la base de donnee")
                return
            
            try:
                api = client.API('arrivages')
                p = {'produit_id':pdt.get('produit_id'),'quantite':piece.get()}
                api.add(p)
                alert_wn(f"'{p.get('quantite')}' pieces du produit '{produit.get()}' ont ete ajoute")
            except Exception as e:
                alert_wn(e)

        self.f = Toplevel()
        self.f.resizable(False,False)
        self.f.geometry("380x240")
        Label(self.f,text="Inserer les arrivages",height=3,font=('Arial',15)).grid(row=0,column=1)
        Label(self.f,text="Produit :").grid(row=1,column=0)
        self.l_produit = ttk.Combobox(self.f,values=list(dict_produits.keys()),textvariable=produit)
        self.l_produit.grid(row=1,column=1)
        Button(self.f,text="Nouveau",command=self.new_produit).grid(row=1,column=2)

        Label(self.f,text='Pieces :').grid(row=2,column=0)
        Entry(self.f,textvariable=piece).grid(row=2,column=1)
        Button(self.f,text="Inserer",command=ret).grid(row=3,column=1)
                                                               
    def new_produit(self):
        n_produit = StringVar()
        categorie = StringVar()
        prix = StringVar() 
        code = StringVar()
        photo = StringVar()

        def ret():
            """Fonction return"""
            name = n_produit.get().strip()
            if not name in dict_produits.keys():
                if prix.get().strip() == "":
                    alert_wn('Le champ produit ne peut être null')
                    return
                
                if name == '':
                    alert_wn('Veillez renseigner le nom du produit')
                    return

                try:
                    api = client.API('produits')
                    p_id = len(dict_produits) + 1
                    cat_id = dict_categries.get(categorie.get())['categorie_id']
                    x = {
                        'label':name,'prix':prix.get(),'categorie_id':cat_id,
                        'code_barre':code.get(),'photo':photo.get(),'description':desc.get('1.0','end-1c'),'produit_id':p_id }
                    api.add(x)
                except Exception as e:
                    alert_wn(e)
                else:
                    self.actualise_prod()

                    alert_wn("Ajouter du produit '{}' avec success".format(n_produit.get()))
                    ff.destroy()
                return 
            
            alert_wn("Le produit {} existe déja".format(n_produit.get()))

        
        ff = Toplevel(self.f,name="arrivage")
        ff.resizable(False,False)

        Label(ff,text='Inserer un nouveau produit ',height=3,font=('Arial',15)).grid(row=0,column=1)

        Label(ff,text="Nom du produit :").grid(row=1,column=0)
        Entry(ff,textvariable=n_produit).grid(row=1,column=1)
        Label(ff,text="Categorie :").grid(row=2,column=0)
        self.cat = ttk.Combobox(ff,values=list(i for i in dict_categries.keys()),textvariable=categorie)
        self.cat.grid(row=2,column=1)
        Button(ff,text='Ajouter une categorie',command=self.add_cat).grid(row=2,column=2)

        Label(ff,text="Prix :").grid(row=3,column=0)
        Entry(ff,textvariable=prix).grid(row=3,column=1)

        Label(ff,text="Photo :").grid(row=4,column=0)
        Entry(ff,textvariable=photo,state='readonly').grid(row=4,column=1)
        Button(ff,text='parcourir').grid(row=4,column=2)

        Label(ff,text="Code barre :").grid(row=5,column=0)
        Entry(ff,textvariable=code).grid(row=5,column=1)

        Label(ff,text="Description :").grid(row=6,column=0)
        desc = Text(ff,height=6,width=20)
        desc.grid(row=6,column=1)

        Button(ff,text="Enregistrer",width=15,command=ret).grid(row=7,column=1)

    def add_cat(self):
        def ret():
            if label.get().strip() == '':
                alert_wn("veillez remplir le champ label")
                return
            
            try:
                api = client.API('categories')
                c_id = len(dict_categries) + 1
                param = {'label':label.get(),'description':desc.get('1.0','end-1c')}
                api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                alert_wn(f"La categorie '{label.get()}' a ete ajouté avec success")
                self.actualise_cat()
                f.destroy()

        label = StringVar()
        f = Toplevel(self.f)
        f.geometry('450x260')
        f.resizable(False,False)

        Label(f,text="Ajouter une nouvelle categorie",height=3,font=('Arial',15)).grid(row=1,column=1)

        Label(f,text="Label : ").grid(row=2,column=0)
        Entry(f,textvariable=label).grid(row=2,column=1)

        Label(f,text="Description : ").grid(row=3,column=0)
        desc = Text(f,height=7,width=17)
        desc.grid(row=3,column=1)

        Button(f,text="Enregistrer",command=ret).grid(row=5,column=1)

    def actualise_cat(self):
        actualise_cat()
        self.cat.config(values=[f for f in dict_categries])

    def actualise_prod(self):
        actualise_prod()
        self.l_produit.config(values=list(dict_produits.keys()))
        
class stock:
    def __init__(self):
        """Ouvre la fenetre pour le stock"""
        self.master = Toplevel()
        self.master.geometry("800x600")
        self.master.resizable(width=False,height=False)

        tab = ttk.Treeview(self.master,columns=('id','marchandise','categorie','quantite','prix'),height=500)
        tab.heading('id',text="Id")
        tab.column('id',width=35)
        tab.heading('marchandise',text='Marchandises')
        tab.heading('categorie',text="Categorie")
        tab.heading('quantite',text="Quantités")
        tab.heading('prix',text="Prix")
        
        tab['show']='headings'
        self.dict_stocks = {}
        try:
            api = client.API('produits')
            data = api.all()        # je dois chercher a inserer ou pourvoir a un mechnisme dactualisation de prod et cat
        except Exception as e:
            alert_wn(e)
            #self.master.destroy()
        else:
            for produit in data:
                p = [
                    produit.get('produit_id'),
                    produit.get('label'),
                    id_name_categories.get(produit.get('categorie_id')),
                    produit.get('quantite'),
                    produit.get('prix'),
                    ]
                tab.insert('','end',values=p)
        
        sc=Scrollbar(self.master,command=tab.yview)
        sc.pack(side="right",fill=Y)

        tab.configure(yscrollcommand=sc.set)

        tab.pack()

class win_client:
    def __init__(self):
        self.window = Toplevel(name='clients')
        self.window.resizable(False,False)

        f1 = Frame(self.window,padx=5,pady=5)
        self.tab = ttk.Treeview(f1,columns=['id','noms','tel','addr'])

        self.tab.heading('id',text='ID client')
        self.tab.heading('noms',text='Nom complet')
        self.tab.heading('tel',text='telephone')
        self.tab.heading('addr',text='Adresse')

        self.tab['show'] = 'headings'

        self.tab.pack()

        sc=Scrollbar(f1,command=self.tab.yview)
        sc.pack(side="right",fill='y')

        self.tab.pack(fill=Y,expand=4)
        self.tab.configure(yscrollcommand=sc.set)

        self.actualise()

        f1.pack()

        f2 = Frame(self.window,padx=5,pady=5)
        Button(f2,text=" Selectionner ",command=self.select,padx=3,pady=3).pack(side='left')
        Button(f2,text=" Ajouter ",command=self.add,padx=3,pady=3).pack(side='left')
        Button(f2,text=" Supprimmer ",command=self.delete,padx=3,pady=3).pack(side='right')
        f2.pack(side='bottom')

    def add(self): # il ne pas achever 
        def ret():
            param = {
                'noms':noms.get(),
                'addr':addr.get(),
                'telephone':tel.get(),
                'nationalite':nat.get(),
                'email':mail.get(),
            }
            try:
                api = client.API('clients')
                data = api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                win.destroy()
                self.actualise()

        win = Toplevel(class_="Ajout",padx=10,pady=10)
        win.resizable(False,False)
        #win.geometry('720x300+10+18')
        noms = StringVar()
        addr = StringVar()
        tel = StringVar()
        mail = StringVar()
        nat = StringVar()

        f1 = Frame(win,padx=15,pady=15)
        Label(f1,text="Noms : ",padx=8,font=('',15)).pack(side='left')
        Entry(f1,textvariable=noms).pack(side='right')
        f1.pack()

        f2 = Frame(win,padx=15,pady=15)
        Label(f2,text="Adresse : ",padx=8,font=('',15)).pack(side='left')
        Entry(f2,textvariable=addr).pack(side='right')
        f2.pack()

        f3 = Frame(win,padx=15,pady=15)
        Label(f3,text="Nationalite : ",padx=8,font=('',15)).pack(side='left')
        Entry(f3,textvariable=nat).pack(side='right')
        f3.pack()

        f5 = Frame(win,padx=15,pady=15)
        Label(f5,text="Telephone : ",padx=8,font=('',15)).pack(side='left')
        Entry(f5,textvariable=tel).pack(side='right')
        f5.pack()

        f6 = Frame(win,padx=15,pady=15)
        Label(f6,text="Email : ",padx=8,font=('',15)).pack(side='left')
        Entry(f6,textvariable=mail).pack(side='right')
        f6.pack()

        Button(win,text="Enregistrer",command=ret,font=('',15)).pack(side='bottom')

    def delete(self): # je dois implementer la confirmation
        try:
            id_ = self.tab.selection()[0]
            api = client.API('clients')
            api.delete(id_)
        except Exception as e:
            alert_wn(e)
        else:
            self.tab.delete(id_)

    def select(self):
        try:
            id_ = self.tab.selection()[0]
        except Exception as e:
            alert_wn("veillez d'abord selectionner le client ")
        else:
            IntVar(value=id_,name='client_id')
            self.window.destroy()

    def actualise(self): 
        try:
            api = client.API('clients')
            data = api.all()
        except Exception as e:
            alert_wn(e)
        else:
            for index , info in data.items():
                p = [
                    info.get('client_id'),
                    info.get('noms'),
                    info.get('telephone'),
                    info.get('addr')
                ]
                self.tab.insert('','end',iid=index,values=p)

    def change(self):
        return

class mainframe():
    def __init__(self,root):
        self.client_id = IntVar(value=1,name='client_id')
        self.tmp_march = {}

        # initialisation des variables
        self.root = root
        self.root.resizable(width=False,height=True)

        ## ces variables sont utiliser pour sauvegarder les entrees utilisateur
        self.var_date = StringVar()
        self.var_date.set(time.strftime("%Y-%m-%d:%H:%M:%S"))
        self.var_marchandise = StringVar()
        self.var_piece = IntVar()
        self.var_piece.set(1)
        self.var_prix = StringVar()
        self.var_vendor = client._cred.get('uname',None)

        self.var_t_prix = StringVar()

        self.error = StringVar()

        ## en-tete qui contient la barre de menu 
        menuBar = Menu(self.root) # ma barred de menu
        #       menu option
        menu_option = Menu(menuBar,tearoff=0)
        menu_option.add_command(label="A propos",command=about)
        menu_option.add_command(label="Importer *")  # no implemeter
        menu_option.add_command(label="Exporter *")# no implemeter
        menu_option.add_command(label="Parametre *")# no implemeter
        menu_option.add_command(label="Quitter",command=self.root.destroy)
        menuBar.add_cascade(menu=menu_option,label="Options")
        
        #       menu gestion
        menu_gestion = Menu(menuBar,tearoff=0)
        menu_gestion.add_command(label="Inventaire",command=inventaire) 
        menu_gestion.add_command(label="Arrivage",command=arrivage)
        menu_gestion.add_command(label="Stock",command=stock)
        menu_gestion.add_command(label="Actualiser",command=self.actualiser)
        menuBar.add_cascade(menu=menu_gestion,label="Gestion")

        #       menu  administrationmenu_outils
        menu_admin = Menu(menuBar,tearoff=0)
        menu_admin.add_command(label="Utilisateurs ",command=users_admin)
        menu_admin.add_command(label="Sessions ",command=session_admin)
        menuBar.add_cascade(menu=menu_admin,label="Administration") 

        #       menu  outils
        menu_outils = Menu(menuBar,tearoff=0)
        menu_outils.add_command(label="calculatrice *") # no implemeter
        menuBar.add_cascade(menu=menu_outils,label="Outils")
        
        self.root.config(menu=menuBar)

        ##      corps de la page 
        body = Frame(self.root)

        # le frame de gauche qui contient la liste
        f_left = Frame(body,width=20,padx=15,pady=15)#,height=200)

        
        f4 = Frame(f_left)
        Label(f4,text="Date :",border='5').pack(side='left')
        Label(f4,textvariable=self.var_date).pack(side='right')
        f4.pack()

        f5 = Frame(f_left)
        Label(f5,text="Non du vendeur  :",border='5').pack(side='left')
        Label(f5,text=self.var_vendor).pack(side='right')
        f5.pack()

        f6 = Frame(f_left)
        Label(f6,text="Id du client  :",border='5').pack(side='left')
        Entry(f6,textvariable='client_id').pack(side='left')
        Button(f6,text=' + ',command=win_client).pack(side='right')
        f6.pack()

        f7 = Frame(f_left)
        Label(f7,text="Marchandises :",border='5').pack(side='left')
        f7.pack()

        f8 = Frame(f_left,height=90,width=135)
        self.lc_temp = ttk.Treeview(f8,columns=('produit','quantite','prix'))#,height=50)
        self.lc_temp.heading('produit',text='Produits')
        self.lc_temp.column('produit',width=80)
        self.lc_temp.heading('quantite',text='Quantite')
        self.lc_temp.column('quantite',width=60)
        self.lc_temp.heading('prix',text='Prix')
        self.lc_temp.column('prix',width=80)
        self.lc_temp['show'] = 'headings'
        self.lc_temp.bind('<Control-D>',self.del_temp)
        self.lc_temp.bind('<Control-d>',self.del_temp)

        self.lc_temp.pack(fill=Y,expand=1)
        f8.pack()

        f9 = Frame(f_left,border=5)
        Label(f9,text='Total :').pack(side='left')
        Label(f9,textvariable=self.var_t_prix).pack(side='right')
        f9.pack()
        
        f10 = Frame(f_left,border=4)
        self.l_march = ttk.Combobox(f10,textvariable=self.var_marchandise,validate='focus') # add values je dois jouter le suggetion
        self.l_march.pack(side='left')
        Entry(f10,textvariable=self.var_piece,width=10).pack(side='left')
        Button(f10,text='Valider',command=self.insert_tab).pack(side='right')
        f10.pack()
        
        f11 = Frame(f_left,border=3)
        Button(f11,text="Nouveau",command=self.nouv_fonc).pack(side='left')
        Button(f11,text="Annuler",command=self.anul_fonc).pack(side='left')
        Button(f11,text="Sauvegarder",command=self.sauv_fonc).pack(side='right')
        f11.pack(side='bottom')
        
        f_left.pack(fill=Y,side='left',padx=5,pady=5)

        # frame de droite 
        f_right = Frame(self.root,padx=10,pady=10)

        self.lc = ttk.Treeview(f_right,columns=('name','vendor','produit','prix','date'))
        self.lc.heading('name',text='Id client')
        self.lc.heading('vendor',text='Vendeur')
        self.lc.column('vendor',width=125)
        self.lc.heading('produit',text='Produit')
        self.lc.heading('prix',text='Prix')
        self.lc.column('prix',width=75)
        self.lc.heading('date',text='Date')
        self.lc.column('date',width=175)
        self.lc['show'] = 'headings'


        sc=Scrollbar(f_right,command=self.lc.yview)
        sc.pack(side="right",fill='y')

        self.lc.pack(fill=Y,expand=4)
        self.lc.configure(yscrollcommand=sc.set)
        
        
        f_right.pack(fill='both',side=RIGHT,expand=1)
        body.pack()


         ## pied ou base de la fenetre  

        #foot = Frame(self.root)
        #Label(self.root,text='',font=('Arial',10),bg='red').pack(fill='y')
        #c = Frame(foot,width=200)
        #    je nai pas encore inserer le voyant

        #c.pack(side='right')
        #foot.pack()#,expand=1)   # apparament cest lui qui est a la base de probleme

        
        
        self.actualiser()

        self.root.mainloop()

    def actualiser(self):
        try:
            actualise_all()
        except Exception as e:
            alert_wn(e)
        else:
            self.l_march.config(values=[x for x in dict_produits.keys()])

    def sauv_fonc(self):
        """rengistre les entrees dans la bd backend"""
        if not self.tmp_march:
            return 
        
        param = {}
        param['marchandises'] = {}


        str_march = ''

        for p_id , qprod_idtab in self.tmp_march.items():
            param['marchandises'].update({p_id:qprod_idtab[0]})
            str_march += f'{id_name_produits[p_id]}({qprod_idtab[0]}) '

        id_client = self.client_id.get()

        if  id_client != '':
            param.update({'client_id':id_client})
        else:
            id_client = 1
            param.update({'client_id':1})

        try:
            api = client.API('ventes')
            api.add(param)

        except Exception as e:
            alert_wn(e)
        else :
            self.lc.insert('','end',values=[
                id_client,
                self.var_vendor,
                str_march,
                self.var_t_prix.get(),
                time.strftime("%Y-%m-%d:%H:%M:%S")
                
            ])
            self.nouv_fonc()
             
    def nouv_fonc(self):
        """reinitialise la valeur des entrees"""
        self.anul_fonc()
        self.var_date.set(time.strftime("%Y-%m-%d:%H:%M:%S"))

    def anul_fonc(self):
        """anulle le entrees utulisateur"""
        self.client_id.set('')
        self.var_date.set(time.strftime("%Y-%m-%d:%H:%M:%S"))
        self.var_marchandise.set('')
        self.var_piece.set('1')
        self.var_prix.set('')
        self.tmp_march.clear()

    def insert_tab(self):
        march = dict_produits.get(self.l_march.get())
        if march.get('produit_id') in dict_produits.keys():
            alert_wn(f"Le produit '{march}' n'existe pas das la base de donnée")
            return
        
        quatite = self.var_piece.get()

        if march.get('produit_id') in self.tmp_march.keys():
            p_id = int(march.get('produit_id'))
            self.tmp_march[p_id][0] += int(quatite)
            self.tmp_march[p_id][1] = march.get('prix') * int(self.tmp_march[p_id][0])
            self.lc_temp.delete(self.tmp_march[p_id][2])
            self.lc_temp.insert('','end',iid=p_id,values=(march.get('label'),self.tmp_march[p_id][0],self.tmp_march[p_id][1]))
        else:
            p_id = int(march.get('produit_id'))
            prix = march.get('prix') * quatite
            self.tmp_march.update({march.get('produit_id'):[quatite,prix]})
            self.lc_temp.insert('','end',iid=p_id,values=(march.get('label'),quatite,prix))

        t = 0
        for x in self.tmp_march.keys():
            t += self.tmp_march[x][1]

        self.var_t_prix.set(t)

    def del_temp(self,event):
        """suprimme un element dans la liste temp"""
        try:
            item = self.lc_temp.selection()[0]
            self.lc_temp.delete(item)
            del self.tmp_march[int(item)]
        except :
            pass
        else:
            t = 0
            for x in self.tmp_march.keys():
                t += self.tmp_march[x][1]

            self.var_t_prix.set(t)
            

    
