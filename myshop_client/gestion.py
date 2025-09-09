from .utils import alert_wn, API, setting, temp_setting, clean_variable, Printer, selecteur_date, askfile_open
from .widgets import *

class VentePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.data = {}
        self.exist_item = []
        # Conteneur principal
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        
        # Création des différentes frames
        for F in (self.Home,):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame('Home')
        
    def show_frame(self, cont,action=''):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        if cont != 'Home':
            clean_variable(frame)
        frame.tkraise()
        
    def Home(self,container):
        frame = Frame(container,background='skyblue',name='frame_home')
                
        somme = IntVar(frame,name='var_somme')
        
        f_top = Frame(frame,background='skyblue',name='frame_top')
        Label(f_top,text="Ventes",font=('',15),background='skyblue').pack(padx=5,pady=5)
        
        f_entry = Frame(f_top,background='skyblue',name='body')
        for name, message in (('vendeur','Vendeur'),('client_id','Id du client'),('from','Date depart') ,('to','Date fin')):
            variable = StringVar(frame,name=f'var_{name}')
            entry = EntryWithLabel(f_entry,variable_text=f'var_{name}',label_text=message,entry_cnf={'name':f'entry_{name}'},frame_name=f'frame_{name}')
            #entry.pack(padx=5,pady=5)
            
        f_entry.nametowidget('frame_from.entry_from').bind('<FocusIn>', lambda event: selecteur_date('var_from',frame))#,entry)) 
        f_entry.nametowidget('frame_to.entry_to').bind('<FocusIn>', lambda event: selecteur_date('var_to',frame))#,entry)) 
        
        Button(f_entry,name='b_search',text= 'Chercher',command = lambda : self.actualise()).pack(side='right',padx=5,pady=5)
        f_entry.pack()

        f_top.pack()

        f2 = Frame(frame,background='skyblue',name='body')
        lc = ttk.Treeview(f2,columns=('id','client_id','march','vendeur','prix'),name='tableau')
        lc.heading('id',text="Id")
        lc.column('id',width=35)
        lc.heading('client_id',text="Client id")
        lc.heading('march',text='Marchandises')
        lc.heading('vendeur',text="Vendeur")
        lc.heading('prix',text="Prix")
        
        lc['show'] = 'headings'
        lc.bind('<Double-Button-1>',self.open)

        sc=Scrollbar(f2,command=lc.yview)
        sc.pack(side="right",fill=Y)

        lc.configure(yscrollcommand=sc.set)
        lc.pack(expand=True,fill='both')

        f2.pack(fill='both',expand=True)

        f3 = Frame(frame,background='skyblue')
        Label(f3,text='Total : ',background='skyblue').pack(side='left')
        Label(f3,textvariable=somme,background='skyblue').pack(side='left')
        f3.pack(padx=5,pady=5)
        
        return frame

    def open(self,event):
        try:
            lc = self.frames['Home'].nametowidget('body.tableau')
            id_ = lc.selection()[0]
            data = self.data.get(id_)
        except Exception as e:
            alert_wn(e)
        else:
           Printer(data)

    def actualise(self):
        try:
            param = {}
            win = self.frames['Home']
            for i in ['vendeur','client_id','from','to']:
                try:
                    name = f'var_{i}'
                    value = win.getvar(name)
                    param[i] = value
                except:
                    continue

            api = API(setting.get('url'),'ventes',cookie=temp_setting.cookie)
            data = api.all(param=param)
        except Exception as e:
            alert_wn(e)
        else:
            self.data.clear()
            self.data.update(data)
            self.frames['Home'].setvar('somme',0)
            lc = self.frames['Home'].nametowidget('body.tableau')
            
            for i in self.exist_item:
                lc.delete(i)

            self.exist_item.clear()

            for i, info in data.items():
                p = (
                    info.get('vente_id'),info.get('client_id'),' | '.join(info.get('marchandises').keys()),
                    info.get('vendeur'),info.get('prix'))
                item = lc.insert('','end',iid=info.get('vente_id'),values=p)
                self.exist_item.append(item)

class StockPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # Conteneur principale
        container = Frame(self,name='root_stock')
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        self.data = {}
        self.data_cat = {}
        self.name_id_categories = {}
        self.temp_index = []
        
        # Création des différentes frames
        for F in (self.Home, self.Add,self.AddCat):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Afficher la première frame
        self.show_frame("Home")

    def show_frame(self,cont,action=''):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        if cont == 'Add':
            clean_variable(frame)
            frame.setvar('var_produit_id','')
        if action:
            tab = self.frames['Home'].nametowidget('body.tableau')
            try:
                id_ = tab.selection()[0]
                data = self.data.get(id_)

                frame.setvar('var_produit_label',data.get('label'))
                frame.setvar('var_produit_id',data.get('produit_id'))
                frame.setvar('var_cat_label',data.get('cat_label'))
                frame.setvar('var_prix_vente',data.get('prix_vente'))
                frame.setvar('var_prix_achat',data.get('prix_achat'))
                frame.setvar('var_date_expiration',data.get('date_expiration'))
                frame.setvar('var_code_barre',data.get('code_barre'))
                frame.setvar('var_photo',data.get('photo'))
                frame.children['body'].children['description'].insert('1.0',data.get('description'))
            except IndexError:
                alert_wn("Veillez d'abord selectionner l'item")
            except Exception as e:
                alert_wn(e)
            
        frame.tkraise()
        
    def actualise(self):
        tab = self.frames['Home'].nametowidget('body.tableau')
        list_cat = self.frames['Add'].nametowidget('body.categorie.list_cat')
        try:
            data_cat = API(setting.get('url'),'categories',cookie=temp_setting.cookie).all()
            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            self.data.update(api.all())
            self.data_cat.update(data_cat)
        except Exception as e:
            alert_wn(e)
        for i, produit in self.data.items():
            p = (
                produit.get('produit_id'),
                produit.get('label'),
                produit.get('cat_label'),
                produit.get('quantite'),
                produit.get('prix_vente'),
                produit.get('date_modification')
            )
            self.temp_index.append(produit.get('produit_id'))
            if tab.exists(int(i)):
                tab.delete(int(i))
                
            tab.insert('','end',iid=produit.get('produit_id'),values=p)

        for i, d in self.data_cat.items():
            self.name_id_categories.update({d.get('label'):d.get('categorie_id')})
        
        list_cat.config(values=[i for i in self.name_id_categories.keys()])

    def Home(self,contenair):
        frame = Frame(contenair,background='skyblue',name='frame_home')
        frame.bind('<Control-F>',self.search)
        frame.bind('<Control-f>',self.search)

        Label(frame,text="Stock",font=('',15),background='skyblue').pack(padx=5,pady=5)

        f1 = Frame(frame,background='skyblue',name='body')
        tab = ttk.Treeview(f1,columns=('id','marchandise','categorie','quantite','prix_vente','date_modification'),name='tableau')

        tab.heading('id',text='ID produit')
        tab.heading('marchandise',text='Nom produit')
        tab.heading('categorie',text='Categorie')
        tab.heading('quantite',text='Quantite')
        tab.heading('prix_vente',text='Prix Vente')
        tab.heading('date_modification',text='Date Modification')
        
        tab['show'] = 'headings'

        sc=Scrollbar(f1,command=tab.yview)
        sc.pack(side="right",fill='y')

        tab.configure(yscrollcommand=sc.set)
        tab.pack(fill='both',expand=True)

        f1.pack(fill='both',expand=True)

        f2 = Frame(frame,padx=5,pady=5,background='skyblue')
        Button(f2,text=" Ajouter ",command=lambda: self.show_frame('Add'),padx=3,pady=3).pack(side='left')
        Button(f2,text=" Voir ",command=lambda: self.show_frame('Add',action='see'),padx=3,pady=3).pack(side='left')
        Button(f2,text=" Supprimmer ",command=self.delete,padx=3,pady=3).pack(side='right')
        f2.pack(side='bottom')
        
        return frame
       
    def search(self,event):
        tab = self.frames['StockHome'].nametowidget('body.tableau')
        def filtre():
            for n in self.temp_index:
                tab.delete(n)

            self.temp_index.clear()
            for i, produit in self.data.items():
                if not name.get().upper() in produit.get('label').upper():
                    continue

                p = (
                    produit.get('produit_id'),
                    produit.get('label'),
                    produit.get('cat_label'),
                    produit.get('quantite'),
                    produit.get('prix'),
                )
                self.temp_index.append(produit.get('produit_id'))
                tab.insert('','end',iid=produit.get('produit_id'),values=p)

        win = Toplevel(background='skyblue')
        name = StringVar()

        Label(win,text="Recherche produit",font=('',15),background='skyblue').pack()

        f1= Frame(win,background='skyblue')
        Label(f1,text='Label : ',background='skyblue').pack(side='left')
        Entry(f1,textvariable=name).pack()

        f1.pack()

        Button(win,text="Chercher",padx=5,pady=5,command=filtre).pack()

    def delete(self): # je dois implementer la confirmation
        tab = self.frames['Home'].nametowidget('body.tableau')
        try:
            id_ = tab.selection()[0]
            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            api.delete(id_)
        except IndexError:
            alert_wn("Veillez d'abord selectionner l'item")
        except Exception as e:
            alert_wn(e)
        else:
            tab.delete(id_)
            self.temp_index.remove(id_)

    def Add(self,contenair):
        def set_photo():
            askfile_open(photo,[('Image File','*.png'),('Image File','*.jpg')])  # un souci avec ctte partie du code 

        def voir():
            image_64 = photo.get()
            if image_64:
                fen = Toplevel(background='skyblue')
                image = PhotoImage(data=image_64)
                Label(fen,text='Image du produit',image=image,compound=LEFT,background='skyblue').pack()
            else:
                alert_wn("Aucune image n'a etait definie ")

        def ret():
            name = n_produit.get().strip()
            if '|' in name:
                alert_wn("Le nom du produit ne peut pas comporter le caractere '|' ")
                return 
                
            if name == '':
                alert_wn('Veillez renseigner le nom du produit')
                return

            try:
                api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
                cat_id = self.name_id_categories.get(categorie.get())
                param = {
                    'label':name,'prix_achat':prix_achat.get(),'prix_vente':prix_vente.get(),'date_expiration':date_expiration.get(),'categorie_id':cat_id,
                    'code_barre':code.get(),'photo':photo.get(),'description':desc.get('1.0','end-1c')
                    }
                if not p_id.get():
                    data = api.add(param)
                else:
                    param.update({'produit_id':p_id.get()})
                    data = api.change(param)
            except Exception as e:
                alert_wn(e)
            else:
                tab = self.frames['Home'].nametowidget('body.tableau')
                data['cat_label'] = categorie.get()
                i_ = str(data.get('produit_id'))
                self.data.update({i_:data})
                p = (
                    data.get('produit_id'),
                    data.get('label'),
                    data.get('cat_label'),
                    data.get('quantite'),
                    data.get('prix_vente'),
                    data.get('date_modification')
                )
                self.temp_index.append(data.get('produit_id'))
                
                if p_id.get():
                    i = tab.selection()
                    tab.delete(i[0])

                tab.insert('','end',iid=data.get('produit_id'),values=p)
                self.show_frame('Home')
                alert_wn("Insertion des infos du produit '{}' avec success".format(n_produit.get()))
        
        frame = Frame(contenair,name='frame_add',background='skyblue')
        n_produit = StringVar(frame,name='var_produit_label')
        categorie = StringVar(frame,name='var_cat_label')
        prix_achat = StringVar(frame,name='var_prix_achat') 
        prix_vente = StringVar(frame,name='var_prix_vente') 
        date_expiration = StringVar(frame,name='var_date_expiration') 
        code = StringVar(frame,name='var_code_barre')
        photo = StringVar(frame,name='var_photo')
        p_id = StringVar(frame,name='var_produit_id')

        Label(frame,text='Inserer un nouveau produit ',height=3,font=('Arial',15),background='skyblue').pack()

        EntryWithLabel(frame,variable_text='var_produit_label',label_text='Nom du produit :')
        EntryWithLabel(frame,variable_text='var_prix_achat',label_text="Prix  d'achat:")
        EntryWithLabel(frame,variable_text='var_prix_vente',label_text="Prix  de vente:")
        date_ex = EntryWithLabel(frame,variable_text='var_date_expiration',label_text="Date expiration:")
        date_ex.bind('<FocusIn>', lambda event: selecteur_date('var_date_expiration',frame)) 
        EntryWithLabel(frame,variable_text='var_code_barre',label_text="Code barre :")

        ff = Frame(frame,name='body',background='skyblue')

        ComboboxWithLabel(ff,label_text='Catagorie :',frame_name='categorie',textvariable=categorie,combox_cnf={'name':'list_cat'})
        Button(ff,text='Ajouter une categorie',command=lambda: self.show_frame('AddCat')).pack(side='right')
        
        Label(ff,text="Description :",background='skyblue').pack()
        desc = Text(ff,height=15,width=25,name='description')
        desc.pack()
        
        f_botton = Frame(ff,background='skyblue')
        Button(f_botton,text="Envoyer",width=15,command=ret).pack(side='left')
        Button(f_botton,text="Annuler",width=15,command=lambda: self.show_frame('Home')).pack(side='right')
        f_botton.pack(side='bottom')
        ff.pack(fill='both',expand=True)
        
        return frame

    def AddCat(self,contenair):
        def ret():
            if label.get().strip() == '':
                alert_wn("veillez remplir le champ label")
                return
            
            try:
                api = API(setting.get('url'),'categories',cookie=temp_setting.cookie)
                param = {'label':label.get(),'description':desc.get('1.0','end-1c')}
                data = api.add(param)
            except IndexError as e:
                alert_wn(e)
            else:
                cat = self.frames['Add'].nametowidget('body.categorie.list_cat')
                self.name_id_categories.update({data.get('label'):data.get('categorie_id')})
                cat.config(values=[n for n,i in self.name_id_categories.items()])
                alert_wn(f"La categorie '{label.get()}' a ete ajouté avec success")
                self.show_frame('Add')

        frame = Frame(contenair,name='frame_cat_add',background='skyblue')
        label = StringVar(frame,name='var_label')

        Label(frame,text="Ajouter une nouvelle categorie",height=3,font=('Arial',15),background='skyblue').pack()
        
        EntryWithLabel(frame,variable_text='var_label',label_text='Label :')

        f2 = Frame(frame)
        Label(f2,text="Description : ",background='skyblue').pack()
        desc = Text(f2,height=15,width=25)
        desc.pack()
        f2.pack()
        
        f3 = Frame(frame)
        Button(f3,text="Ajouter",command=ret).pack(side='left')
        Button(f3,text="Annuler",command=lambda : self.show_frame('Add')).pack(side='right')
        f3.pack(side='bottom')
        return frame

class ArrivagePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.data = {}
        self.produits = {}
        self.produits_label_id = {}
        self.temp_index = []
        # Conteneur principal
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        
        # Création des différentes frames
        for F in (self.Add, self.Home):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame('Home')
    
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        if frame != 'Home':
            clean_variable(frame)
        frame.tkraise()

    def Home(self,contenair):
        frame = Frame(contenair,background='skyblue',name='frame_home')
        frame.bind("<Control-f>" or "<Control-F>",self.search)
        frame.bind("<Control-A>" or "<Control-a>",self.actualise)

        Label(frame,text="Arrivages",font=('',15),background='skyblue').pack(padx=5,pady=5)

        f1 = Frame(frame,background='skyblue',name='body')
        tab = ttk.Treeview(f1,columns=('id','produit','quantite','date'),name='tableau')

        tab.heading('id',text='ID ')
        tab.heading('produit',text='produit')
        tab.heading('quantite',text='Quantite')
        tab.heading('date',text='Date')

        tab['show'] = 'headings'

        sc=Scrollbar(f1,command=tab.yview)
        sc.pack(side="right",fill='y')

        tab.configure(yscrollcommand=sc.set)
        tab.pack(fill="both", expand=True)

        f1.pack(fill="both", expand=True)

        f2 = Frame(frame,padx=5,pady=5,background='skyblue',name='bottom')
        Button(f2,text=" Ajouter ",command=lambda: self.show_frame("Add") ,padx=3,pady=3).pack(side='left')
        #Button(f2,text=" Voir ",command=self.see,padx=3,pady=3).pack(side='left')
        Button(f2,text=" Supprimmer ",command=self.delete,padx=3,pady=3).pack(side='right')
        f2.pack(side='bottom')
        
        return frame

    def actualise(self):
        try:
            api = API(setting.get('url'),'arrivages',cookie=temp_setting.cookie)
            self.data.clear()
            self.data.update(api.all())

            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            produits = api.all()
        except Exception as e:
            alert_wn(e)
        else:
            self.produits_label_id.clear()
            self.temp_index.clear()

            tab = self.frames['Home'].nametowidget('body.tableau')
            for i , d in self.data.items():
                p = (
                    d.get('arrivage_id'),d.get('label'),d.get('quantite'),d.get('date'),
                )
                if tab.exists(int(i)):
                    tab.delete(int(i))

                tab.insert('','end',iid=d.get('arrivage_id'),values=p)
                self.temp_index.append(d.get('arrivage_id'))

            for id_ , info in produits.items():
                self.produits_label_id.update({info.get('label'):id_})
          
    def search(self,event):
        tab = self.frames['Home'].nametowidget('body.tableau')
        def filtre():
            try:
                param = {
                    'label':label.get(),
                }
                arrivages = API(setting.get('url'),'arrivages',cookie=temp_setting.cookie).all(param=param)
            except Exception as e:
                alert_wn(e)
                return

            for n in self.temp_index:
                tab.delete(n)

            self.temp_index.clear()
            for i, arriv in arrivages.items():

                p = (
                    arriv.get('arrivage_id'),
                    arriv.get('label'),
                    arriv.get('quantite'),
                    arriv.get('date')
                    )
                self.temp_index.append(arriv.get('arrivage_id'))
                tab.insert('','end',iid=arriv.get('arrivage_id'),values=p)

        win = Toplevel(background='skyblue')
        win.resizable(False,False)
        label = StringVar()

        Label(win,text="Recherche Arrivage",font=('',15),background='skyblue').pack()

        f1 = Frame(win,background='skyblue')
        Label(f1,text='Label : ',background='skyblue').pack(side='left')
        Entry(f1,textvariable=label).pack()
        f1.pack()

        Button(win,text="Chercher",padx=5,pady=5,command=filtre).pack()
    
    def Add(self,contenair):
        """Ajout des arrivages (marchandises, piece , prix, date)"""
             
        def check(e):
            prod = entry.get()
            if not prod:
                return
        
            if prod == '':
                data = self.produits_label_id
            else:
                data = {}
                for d, i in self.produits_label_id.items():
                    if prod.lower() in d.lower():
                        data[i] = d
            try:
                update(data)
            except:
                pass

        def update(data):
            l_march.delete(0,END)
            for i, value in data.items():
                l_march.insert(i,value)

        def delete(event):
            id_ = l_march.curselection()
            prod = l_march.get(id_[0])
            produit.set(prod)
            #entry.config(state='readonly')
            #f2.destroy()

        def ret():
            produit_id = self.produits_label_id.get(produit.get())

            try:
                p = {'produit_id':produit_id,'quantite':piece.get()}
                api = API(setting.get('url'),'arrivages',cookie=temp_setting.cookie)
                data = api.add(p)
                alert_wn(f"{p.get('quantite')} pieces du produit '{produit.get()}' ont été ajouté")
            except Exception as e:
                alert_wn(e)
            else:
                self.data.update(data)
                tab = self.frames['Home'].nametowidget('body.tableau')
                p = (
                    data.get('arrivage_id'),
                    produit.get(),
                    data.get('quantite'),
                    data.get('date')
                )
                tab.insert('','end',iid=data.get('arrivage_id'),values=p)
                self.temp_index.append(data.get('arrivage_id'))
                self.show_frame("Home")

        frame = Frame(contenair,background='skyblue',name='frame_add')
        
        produit = StringVar(frame,name='var_produit')
        piece = IntVar(frame,name='var_piece')
            
        Label(frame,text="Inserer les arrivages",height=3,font=('Arial',15),background='skyblue').pack()

        entry = EntryWithLabel(frame,variable_text='var_produit',label_text="Produit :")
        entry.bind('<KeyRelease>',check)
        entry.pack(side='right')
        
        f2 = Frame(frame,border=4,background='skyblue',name='f2')
        l_march = Listbox(f2,height=10,width=25)
        l_march.bind('<Double-Button-1>',delete)
        l_march.pack()
        f2.pack()

        EntryWithLabel(frame,variable_text='var_piece',label_text="Pieces :").pack()
        
        f4 = Frame(frame,background='skyblue',name='f4')
        Button(f4,text="Inserer",command=ret).pack(side='left')
        Button(f4,text="Retour",command=lambda : self.show_frame('Home')).pack(side='left')
        
        f4.pack(side='bottom')
        
        return frame

    def delete(self): # je dois implementer la confirmation
        try:
            tab = self.frames['Home'].nametowidget('body.tableau')
            id_ = tab.selection()[0]
            api = API(setting.get('url'),'arrivages',cookie=temp_setting.cookie)
            api.delete(id_)
        except IndexError:
            alert_wn("Veillez d'abord selectionner l'item")
        except Exception as e:
            alert_wn(e)
        else:
            tab.delete(id_)
            self.temp_index.remove(id_)

class PromotionPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.produits = {}
        self.data = {}
        self.temp_num_id = {}
        # Conteneur principal
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        
        # Création des différentes frames
        for F in (self.Add, self.Home):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame('Home')
        
    def show_frame(self, cont,action=''):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        send_button = self.frames['Add'].nametowidget('bottom.send_button')
        list_prod = self.frames['Add'].nametowidget('body.list_produit')
        list_prod_select = self.frames['Add'].nametowidget('body.list_produit_select')
        button_plus = self.frames['Add'].nametowidget('body.button_plus')
        button_moins = self.frames['Add'].nametowidget('body.button_moins')
        list_prod_select.delete(0,END)
        if cont != 'Home' and not action:
            clean_variable(frame)
            list_prod.config(state='normal')
            send_button.config(state='active')
            button_plus.config(state='active')
            button_moins.config(state='active')
            list_prod.delete(0,END)
            
            for i , value in enumerate(self.produits.values()):
                self.temp_num_id[i] = value.get('produit_id')
                list_prod.insert(i,value.get('label'))
        elif action:
            clean_variable(frame)
            tab = self.frames['Home'].nametowidget('body.tableau')
            try:
                id_ = tab.selection()[0]
                data = self.data.get(id_)
                send_button.config(state='disabled')
                list_prod.config(state='disabled')
                button_plus.config(state='disabled')
                button_moins.config(state='disabled')
            except IndexError:
                alert_wn("Veillez d'abord selectionner l'item")
            except Exception as e:
                alert_wn(e)
            else:
                produits = data.get('produits_label')
                frame.setvar('var_name',data.get('label'))
                frame.setvar('var_reduction',data.get('reduction'))
                frame.setvar('var_date_f',data.get('date_fin'))
                frame.setvar('var_date_d',data.get('date_debut'))
                frame.children['body'].children['description'].insert('1.0',data.get('description'))
                
                for i, value in enumerate(produits):
                    list_prod_select.insert(str(i),value)
                
        frame.tkraise()
        
    def actualise(self):
        try:
            api = API(setting.get('url'),'promotions',cookie=temp_setting.cookie)
            data = api.all()
 
            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            dt = api.all()
            self.produits.update(dt)
        except Exception as e:
            alert_wn(e)
        else:
            self.data.clear()
            self.data.update(data)
            tab = self.frames['Home'].nametowidget('body.tableau')
            list_prod = self.frames['Add'].nametowidget('body.list_produit')
            list_prod_select = self.frames['Add'].nametowidget('body.list_produit_select')
            
            list_prod_select.delete(0,END)
            list_prod.delete(0,END)
            
            for i , d in data.items():
                p = (
                     d.get('promotion_id'), d.get('label'),
                     ' | '.join(d.get('produits_label')),d.get('reduction'), d.get('date_fin'))
                
                if not tab.exists(int(i)):
                    tab.delete(int(i))

                tab.insert('','end',iid=d.get('promotion_id'),values=p)
                    
    def Home(self,container):
        frame = Frame(container,name='frame_home',background='skyblue')

        Label(frame,text="Promotions",font=('',15),background='skyblue').pack(padx=5,pady=5)

        f1 = Frame(frame,background='skyblue',name='body')
        tab = ttk.Treeview(f1,columns=('id','occasion','produits','reduction','fin'),name='tableau')

        tab.heading('id',text='ID')
        tab.heading('occasion',text='Occasion')
        tab.heading('produits',text='Produits')
        tab.heading('reduction',text='reduction')
        tab.heading('fin',text='Fin')
        
        tab['show'] = 'headings'

        sc=Scrollbar(f1,command=tab.yview)
        sc.pack(side="right",fill='y')

        
        tab.configure(yscrollcommand=sc.set)
        tab.pack(fill='both',expand=True)

        f1.pack(fill='both',expand=True)

        f2 = Frame(frame,padx=5,pady=5,background='skyblue',name='frame_bottom')
        Button(f2,text=" Ajouter ",command=lambda : self.show_frame('Add'),padx=3,pady=3).pack(side='left')
        Button(f2,text=" Voir ",command=lambda : self.show_frame('Add',action='see'),padx=3,pady=3).pack(side='left')
        Button(f2,text=" Supprimmer ",command=self.delete,padx=3,pady=3).pack(side='right')
        f2.pack(side='bottom')
        
        return frame
    
    def Add(self,container):
        p_id_list = []
        def add_produit():
            try:
                march = p_list.curselection()[0]
                label = p_list.selection_get()
                id_ = p_list.index(march)
                
                if not march in p_id_list:
                    
                    p_id_list.append(self.temp_num_id.get(id_))
                    p_list_select.insert(id_,label)
            except IndexError: 
                alert_wn("Veillez d'abord selectionner le produit a ajouté")
            except Exception as e:
                alert_wn(e)
            
        def del_produit():
            try:
                march = p_list_select.curselection()[0]
                label = p_list_select.selection_get()
                id_ = p_list_select.index(march)
                p_id_list.remove(self.temp_num_id.get(id_))
                p_list_select.delete(march)
            except IndexError:
                alert_wn("Veillez d'abord selectionner le produit a rectiré")
            except Exception as e:
                alert_wn(e)

        def ret():
            param = {
                'produits_ids':p_id_list,
                'label':name.get(),
                'date_fin':date_f.get(),
                'date_depart': date_d.get(),
                'description':desc.get('1.0','end-1c'),
                'reduction':reduction.get()
            }

            try:
                api = API(setting.get('url'),'promotions',cookie=temp_setting.cookie)
                data = api.add(param)
                #data.update({'produits_label':' || '.join(p_labels)})
            except Exception as e:
                alert_wn(e)
            else:
                p_id_list.clear()
                p_list_select.delete(0,END)
                tab = self.frames['Home'].nametowidget('body.tableau')
                self.data.update({str(data.get('promotion_id')):data})

                p = (
                    data.get('promotion_id'),
                    data.get('label'),
                    data.get('produits_label'),
                    data.get('reduction'),
                    data.get('date_fin'))
                
                tab.insert('','end',iid=data.get('promotion_id'),values=p)
                self.show_frame('Home')

        frame = Frame(container,background='skyblue',name='frame_add')
        Label(frame,text="Creation d'une promotion",background='skyblue',font=('',17)).pack()
        
        add_entry = StringVar(frame,name='var_add_entry')
        
        name = StringVar(frame,name='var_name')
        reduction = StringVar(frame,name='var_reduction')
        date_f = StringVar(frame,name='var_date_f')
        date_d = StringVar(frame,name='var_date_d')
        
        EntryWithLabel(frame,variable_text='var_name',label_text="Titre :")
        EntryWithLabel(frame,variable_text='var_reduction',label_text='% de la reduction :')
        entry_debut = EntryWithLabel(frame,variable_text='var_date_d',label_text="Date du debut :")
        entry_debut.bind('<FocusIn>', lambda event: selecteur_date('var_date_d',frame))

        entry_fin = EntryWithLabel(frame,variable_text='var_date_f',label_text="Date de fin :")
        entry_fin.bind('<FocusIn>', lambda event: selecteur_date('var_date_f',frame))

        f_body = Frame(frame,background='skyblue',name='body')
        Label(f_body,text="Produits :",background='skyblue',padx=3,pady=3).grid(column=0,row=6)
        p_list = Listbox(f_body,height=8,width=20,name='list_produit')
        p_list.grid(column=1,row=6)
        Button(f_body,padx=5,pady=5,text='+',height=3,width=3,command=add_produit,name='button_plus').grid(column=2,row=6)
        p_list_select = Listbox(f_body,height=8,width=20,name='list_produit_select')
        p_list_select.grid(column=3,row=6)
        Button(f_body,padx=5,pady=5,text='-',height=3,width=3,command=del_produit,name='button_moins').grid(column=4,row=6)
            
        Label(f_body,text="Descripton :",background='skyblue',padx=3,pady=3).grid(column=0,row=7)
        desc = Text(f_body,width=20,height=8,name='description')
        desc.grid(column=1,row=7)
        
        f_body.pack(padx=15,pady=15,expand=True)
        
        f_bottom = Frame(frame,background='skyblue',name='bottom')
        Button(f_bottom,text="Envoyer",command=ret,name='send_button').pack(side='left')
        Button(f_bottom,text="Retour",command=lambda: self.show_frame('Home')).pack(side='right')
        f_bottom.pack(side='bottom',padx=5,pady=5)
        
        return frame

    def delete(self): # je dois implementer la confirmation
        try:
            tab = self.frames['Home'].nametowidget('body.tableau')
            id_ = tab.selection()[0]
            api = API(setting.get('url'),'promotions',cookie=temp_setting.cookie)
            api.delete(id_)
        except IndexError:
            alert_wn("Veillez selectionner la promotion a supprimée")
        except Exception as e:
            alert_wn(e)
        else:
            tab.delete(id_)

