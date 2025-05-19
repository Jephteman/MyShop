from .utils import *
from tkinter import *
from tkinter import ttk

class inventaire:
    def __init__(self):
        self.data = {}
        self.exist_item = []

        self.window = Toplevel(class_="inventaire",width=500,padx=5,pady=5,background='skyblue')
        self.window.resizable(False,False)
        self.window.bind('<Control-f>',self.seek)
        self.window.bind('<Control-F>',self.seek)

        Label(self.window,text="Inventaire",font=('',15)).pack(padx=5,pady=5)
        
        # en-tete  
        self.somme = IntVar()

        f2 = Frame(self.window,background='skyblue')
        self.lc = ttk.Treeview(f2,columns=('id','client_id','march','vendeur','prix'))
        self.lc.heading('id',text="Id")
        self.lc.column('id',width=35)
        self.lc.heading('client_id',text="Client id")
        self.lc.heading('march',text='Marchandises')
        self.lc.heading('vendeur',text="Vendeur")
        self.lc.heading('prix',text="Prix")
        
        self.lc['show'] = 'headings'
        self.lc.bind('<Double-Button-1>',self.open)

        sc=Scrollbar(f2,command=self.lc.yview)
        sc.pack(side="right",fill=Y)

        self.lc.configure(yscrollcommand=sc.set)
        self.lc.pack(expand=1,fill=X)

        f2.pack(fill=Y,expand=1)

        f3 = Frame(self.window,background='skyblue')
        Label(f3,text='Total : ').pack(side='left')
        Label(f3,textvariable=self.somme).pack(side='left')
        f3.pack()

        self.find()

    def open(self,event):
        try:
            id_ = self.lc.selection()[0]
            data = self.data.get(id_)
        except:
            pass
        else:
           Printer(data)

    def find(self,**event):
        try:
            param = {}
            for i in ['vendeur','client_id','from','to']:
                try:
                    value = self.window.getvar(i)
                except:
                    continue
                param[i] = value

            if not param:
                param = {'isform':False}
            else:
                param['isform'] = True

            api = API(setting.get('url'),'ventes',cookie=temp_setting.cookie)
            data = api.all(param=param)
        except Exception as e:
            alert_wn(e)
        else:
            self.data.clear()
            self.data.update(data)
            self.somme.set(0)
            
            for i in self.exist_item:
                self.lc.delete(i)

            self.exist_item.clear()

            for i, info in data.items():
                p = [
                    info.get('vente_id'),info.get('client_id'),' | '.join(info.get('marchandises').keys()),
                    info.get('vendeur'),info.get('prix')]
                item = self.lc.insert('','end',iid=info.get('vente_id'),values=p)
                self.exist_item.append(item)

    def seek(self,event):
        win = Toplevel(background='skyblue')
        win.resizable(False,False)
        Label(win,text='Filtre du resultat',font=('',14)).pack()

        for i in ['vendeur','client_id','from','to']:
            f1 = Frame(win,background='skyblue')
            StringVar(win,name=i)
            Label(f1,text=i).pack(side='left')
            Entry(f1,textvariable=i).pack(side='right')
            f1.pack()

        Button(win,text='Chercher',command=self.find).pack()

class stock:
    def __init__(self):
        self.data = {}
        self.data_cat = {}
        self.name_id_categories = {}
        self.temp_index = []
        self.window = Toplevel(class_='stock',background='skyblue')
        self.window.resizable(False,False)
        try:
            data_cat = API(setting.get('url'),'categories',cookie=temp_setting.cookie).all()
            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            self.data.update(api.all())
            self.data_cat.update(data_cat)
        except Exception as e:
            alert_wn(e)
        
        self.frame1()
        
    def frame1(self):
        self.frame = Frame(self.window) 
        self.frame.bind('<Control-F>',self.search)
        self.frame.bind('<Control-f>',self.search)

        Label(self.frame,text="Stock",font=('',15)).pack(padx=5,pady=5)

        f1 = Frame(self.frame,background='skyblue')
        self.tab = ttk.Treeview(f1,columns=('id','marchandise','categorie','quantite','prix'))

        self.tab.heading('id',text='ID produit')
        self.tab.heading('marchandise',text='Nom produit')
        self.tab.heading('categorie',text='Categorie')
        self.tab.heading('quantite',text='Quantite')
        self.tab.heading('prix',text='Prix')
        
        self.tab['show'] = 'headings'

        sc=Scrollbar(f1,command=self.tab.yview)
        sc.pack(side="right",fill='y')

        
        self.tab.configure(yscrollcommand=sc.set)
        self.tab.pack(fill=Y,expand=4)

        f1.pack()

        f2 = Frame(self.frame,padx=5,pady=5,background='skyblue')
        Button(f2,text=" Ajouter ",command=self.add,padx=3,pady=3).pack(side='left')
        Button(f2,text=" Voir ",command=self.see,padx=3,pady=3).pack(side='left')
        Button(f2,text=" Supprimmer ",command=self.delete,padx=3,pady=3).pack(side='right')
        f2.pack(side='bottom')
        
        self.frame.pack()

        for i, produit in self.data.items():
            p = (
                produit.get('produit_id'),
                produit.get('label'),
                produit.get('cat_label'),
                produit.get('quantite'),
                produit.get('prix'),
            )
            self.temp_index.append(produit.get('produit_id'))
            self.tab.insert('','end',iid=produit.get('produit_id'),values=p)

        for i, d in self.data_cat.items():
            self.name_id_categories.update({d.get('label'):d.get('categorie_id')})
        
       
    def search(self,event):

        def filtre():
            for n in self.temp_index:
                self.tab.delete(n)

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
                self.tab.insert('','end',iid=produit.get('produit_id'),values=p)


        win = Toplevel(background='skyblue')
        name = StringVar()

        Label(win,text="Recherche produit",font=('',15)).pack()

        f1= Frame(win,background='skyblue')
        Label(f1,text='Label : ').pack(side='left')
        Entry(f1,textvariable=name).pack()

        f1.pack()

        Button(win,text="Chercher",padx=5,pady=5,command=filtre).pack()

    def delete(self): # je dois implementer la confirmation
        try:
            id_ = self.tab.selection()[0]
            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            api.delete(id_)
        except IndexError:
            pass
        except Exception as e:
            alert_wn(e)
        else:
            self.tab.delete(id_)
            self.temp_index.remove(id_)

    def see(self):
        def set_photo():
            askfile_open(photo,[('Image File','*.png'),('Image File','*.jpg')])
        
        def voir():
            fen = Toplevel(background='skyblue')
            image_64 = photo.get()
            image = PhotoImage(data=image_64.encode())
            Label(fen,text='Image du produit',image=image,compound=LEFT).pack()

        try:
            id_ = self.tab.selection()[0]
            data = self.data.get(id_)
        except IndexError:
            alert_wn("Veillez d'abord selectionner le client ")
        except InterruptedError as e:
            alert_wn(e)
            return
        else:
        
            p_id = data.get('produit_id')
            n_produit = StringVar(value=data.get('label'))
            categorie = StringVar(value=data.get('cat_label'))
            prix = StringVar(value=data.get('prix')) 
            code = StringVar(value=data.get('code_barre'))
            photo = StringVar(value=data.get('photo'))
            
            def annuler():
                self.frame.destroy()
                self.frame1()

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
                        'label':name,'prix':prix.get(),'categorie_id':cat_id,'produit_id':p_id,
                        'code_barre':code.get(),'photo':photo.get(),'description':desc.get('1.0','end-1c')
                        }
                    if param.get('photo'):
                        with open(param.get('photo')) as f:
                            d = f.read()
                            param['photo'] = base64.b64encode(d)
                    data = api.change(param)
                except Exception as e:
                    alert_wn(e)
                else:
                    data['cat_label'] = categorie.get()
                    i_ = str(data.get('produits'))
                    self.data.update({i_:data})
                    p = (
                        data.get('produit_id'),
                        data.get('label'),
                        data.get('cat_label'),
                        data.get('quantite'),
                        data.get('prix'),
                    )
                    self.tab.insert('','end',iid=data.get('produit_id'),values=p)

                    alert_wn("Ajouter du produit '{}' avec success".format(n_produit.get()))
                    self.frame.destroy()
                    self.frame1()

            self.frame.destroy()
            self.frame = Frame(self.window) 
            ff = Frame(self.frame,background='skyblue')

            Label(ff,text='Information sur le produit ',height=3,font=('Arial',15)).grid(row=0,column=1)

            Label(ff,text="Nom du produit :").grid(row=1,column=0)
            Entry(ff,textvariable=n_produit).grid(row=1,column=1)
            Label(ff,text="Categorie :").grid(row=2,column=0)
            self.cat = ttk.Combobox(ff,values=[i for i in self.name_id_categories.keys()],textvariable=categorie)
            self.cat.grid(row=2,column=1)

            Label(ff,text="Prix :").grid(row=3,column=0)
            Entry(ff,textvariable=prix).grid(row=3,column=1)

            #Label(ff,text="Photo :").grid(row=4,column=0)
            #Entry(ff,textvariable=photo,state='readonly').grid(row=4,column=1)
            #f = Frame(ff)
            #Button(ff,text=' parcourir ',command=set_photo).grid(row=4,column=1)
            #Button(ff,text=" Voir ",command=voir).grid(row=4,column=3)

            Label(ff,text="Code barre :").grid(row=5,column=0)
            Entry(ff,textvariable=code).grid(row=5,column=1)

            Label(ff,text="Description :").grid(row=6,column=0)
            desc = Text(ff,height=6,width=20)
            desc.insert('end-1c',data.get('description'))
            desc.grid(row=6,column=1)
            
            f7 = Frame(ff)
            Button(ff,text="Ajouter",width=15,command=ret).pack(side='left')
            Button(ff,text="Ajouter",width=15,command=annuler).pack(side='right')
            f7.grid(row=7,column=1)
            
            self.frame.pack()

    def add(self):
        def set_photo():
            askfile_open(photo,[('Image File','*.png'),('Image File','*.jpg')])

        def voir():
            fen = Toplevel(background='skyblue')
            image_64 = photo.get()
            image = PhotoImage(data=image_64)
            Label(fen,text='Image du produit',image=image,compound=LEFT).pack()

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
                    'label':name,'prix':prix.get(),'categorie_id':cat_id,
                    'code_barre':code.get(),'photo':photo.get(),'description':desc.get('1.0','end-1c')
                    }
                if param.get('photo'):
                    with open(param.get('photo'),'rb') as f:
                        f = base64.encodebytes(f.read())
                        param['photo'] = f.decode()
                        
                data = api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                data['cat_label'] = categorie.get()
                i_ = str(data.get('produit_id'))
                self.data.update({i_:data})
                p = (
                    data.get('produit_id'),
                    data.get('label'),
                    data.get('cat_label'),
                    data.get('quantite'),
                    data.get('prix'),
                )
                print(data)
                print(p)
                self.temp_index.append(data.get('produit_id'))
                self.tab.insert('','end',iid=data.get('produit_id'),values=p)

                alert_wn("Ajouter du produit '{}' avec success".format(n_produit.get()))
                self.frame.destroy()
                self.frame1()
                
        def annuler():
            self.frame.destroy()
            self.frame1()
            
        n_produit = StringVar()
        categorie = StringVar()
        prix = StringVar() 
        code = StringVar()
        photo = StringVar()
        
        self.frame.destroy()
        self.frame = Frame(self.window)
        ff = Frame(self.frame)

        Label(ff,text='Inserer un nouveau produit ',height=3,font=('Arial',15)).grid(row=0,column=1)

        Label(ff,text="Nom du produit :").grid(row=1,column=0)
        Entry(ff,textvariable=n_produit).grid(row=1,column=1)
        Label(ff,text="Categorie :").grid(row=2,column=0)
        self.cat = ttk.Combobox(ff,values=[i for i in self.name_id_categories.keys()],textvariable=categorie)
        self.cat.grid(row=2,column=1)
        Button(ff,text='Ajouter une categorie',command=self.add_cat).grid(row=2,column=2)

        Label(ff,text="Prix :").grid(row=3,column=0)
        Entry(ff,textvariable=prix).grid(row=3,column=1)

        #Label(ff,text="Photo :").grid(row=4,column=0)
        #Entry(ff,textvariable=photo,state='readonly').grid(row=4,column=1)
        #Button(ff,text='parcourir',command=set_photo).grid(row=4,column=2)
        #Button(ff,text=" Voir ",command=voir).grid(row=4,column=3)

        Label(ff,text="Code barre :").grid(row=5,column=0)
        Entry(ff,textvariable=code).grid(row=5,column=1)

        Label(ff,text="Description :").grid(row=6,column=0)
        desc = Text(ff,height=6,width=20)
        desc.grid(row=6,column=1)
        
        f_botton = Frame(ff)
        Button(f_botton,text="Ajouter",width=15,command=ret).pack(side='left')
        Button(f_botton,text="Annuler",width=15,command=annuler).pack(side='right')
        f_botton.grid(row=7,column=1)
        ff.pack()
        self.frame.pack()

    def add_cat(self):
        def ret():
            if label.get().strip() == '':
                alert_wn("veillez remplir le champ label")
                return
            
            try:
                api = API(setting.get('url'),'categories',cookie=temp_setting.cookie)
                param = {'label':label.get(),'description':desc.get('1.0','end-1c')}
                data = api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                self.name_id_categories.update({data.get('label'):data.get('categorie_id')})
                self.cat.config(values=[n for n,i in self.name_id_categories.items()])
                alert_wn(f"La categorie '{label.get()}' a ete ajouté avec success")
                f.destroy()

        label = StringVar()
        f = Toplevel(background='skyblue')
        f.geometry('450x260')
        f.resizable(False,False)

        Label(f,text="Ajouter une nouvelle categorie",height=3,font=('Arial',15)).grid(row=1,column=1)

        Label(f,text="Label : ").grid(row=2,column=0)
        Entry(f,textvariable=label).grid(row=2,column=1)

        Label(f,text="Description : ").grid(row=3,column=0)
        desc = Text(f,height=7,width=17)
        desc.grid(row=3,column=1)

        Button(f,text="Ajouter",command=ret).grid(row=5,column=1)

class arrivage:
    def __init__(self):
        self.data = {}
        self.produits = {}
        self.temp_index = []
        self.window = Toplevel(class_='clients',background='skyblue')
        self.window.resizable(False,False)
        self.window.bind("<Control-f>",self.search)
        self.window.bind("<Control-F>",self.search)

        Label(self.window,text="Arrivages",font=('',15)).pack(padx=5,pady=5)

        f1 = Frame(self.window,background='skyblue')
        self.tab = ttk.Treeview(f1,columns=('id','produit','quantite','date'))

        self.tab.heading('id',text='ID ')
        self.tab.heading('produit',text='produit')
        self.tab.heading('quantite',text='Quantite')
        self.tab.heading('date',text='Date')
        
        self.tab['show'] = 'headings'

        sc=Scrollbar(f1,command=self.tab.yview)
        sc.pack(side="right",fill='y')

        
        self.tab.configure(yscrollcommand=sc.set)
        self.tab.pack(fill=Y,expand=4)

        f1.pack()

        f2 = Frame(self.window,padx=5,pady=5,background='skyblue')
        Button(f2,text=" Ajouter ",command=self.add,padx=3,pady=3).pack(side='left')
        #Button(f2,text=" Voir ",command=self.see,padx=3,pady=3).pack(side='left')
        Button(f2,text=" Supprimmer ",command=self.delete,padx=3,pady=3).pack(side='right')
        f2.pack(side='bottom')


        try:
            api = API(setting.get('url'),'arrivages',cookie=temp_setting.cookie)
            self.data.update(api.all())

            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            produits = api.all()
        except Exception as e:
            alert_wn(e)
        else:
            for i , d in self.data.items():
                p = (
                    d.get('arrivage_id'),d.get('label'),d.get('quantite'),d.get('date'),
                )
                self.tab.insert('','end',iid=d.get('arrivage_id'),values=p)
                self.temp_index.append(d.get('arrivage_id'))

            for id_ , info in produits.items():
                self.produits.update({info.get('label'):id_})

    def search(self,event):
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
                self.tab.delete(n)

            self.temp_index.clear()
            
            for i, arriv in arrivages.items():

                p = (
                    arriv.get('arrivage_id'),
                    arriv.get('label'),
                    arriv.get('quantite'),
                    arriv.get('date')
                    )
                self.temp_index.append(arriv.get('arrivage_id'))
                self.tab.insert('','end',iid=arriv.get('arrivage_id'),values=p)

        win = Toplevel(background='skyblue')
        win.resizable(False,False)
        label = StringVar()

        Label(win,text="Recherche Arrivage",font=('',15)).pack()

        f1 = Frame(win,background='skyblue')
        Label(f1,text='Label : ').pack(side='left')
        Entry(f1,textvariable=label).pack()
        f1.pack()

        Button(win,text="Chercher",padx=5,pady=5,command=filtre).pack()
    
    def add(self):
        """Ajout des arrivages (marchandises, piece , prix, date)"""

        produits = {}

        try:
            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
        except Exception as e:
            alert_wn(e)
        else:
            for id_ , data in api.all().items():
                label = data.get('label')
                produits.update({label:id_})

        def check(e):
            prod = entry.get()
            if not prod:
                return
        
            if prod == '':
                data = produits
            else:
                data = {}
                for d, i in produits.items():
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
            entry.config(state='readonly')
            f2.destroy()

        produit = StringVar()
        piece = IntVar()

        def ret():
            produit_id = produits.get(produit.get())

            try:
                p = {'produit_id':produit_id,'quantite':piece.get()}
                api = API(setting.get('url'),'arrivages',cookie=temp_setting.cookie)
                data = api.add(p)
                alert_wn(f"{p.get('quantite')} pieces du produit '{produit.get()}' ont été ajouté")
            except Exception as e:
                alert_wn(e)
            else:
                self.data.update(data)
                p = (
                    data.get('arrivage_id'),
                    produit.get(),
                    data.get('quantite'),
                    data.get('date')
                )
                self.tab.insert('','end',iid=data.get('arrivage_id'),values=p)
                self.temp_index.append(data.get('arrivage_id'))
                self.f.destroy()

        self.f = Toplevel(background='skyblue')
        self.f.resizable(False,False)
        self.f.geometry("380x240")
        Label(self.f,text="Inserer les arrivages",height=3,font=('Arial',15)).pack()

        f1 = Frame(self.f,background='skyblue')
        Label(f1,text="Produit :").pack(side='left')
        entry = Entry(f1,textvariable=produit)
        entry.bind('<KeyRelease>',check)
        entry.pack(side='right')
        f1.pack()
        
        f2 = Frame(self.f,border=4,background='skyblue')
        l_march = Listbox(f2,height=10,width=25)
        l_march.bind('<Double-Button-1>',delete)
        l_march.pack()
        f2.pack()

        f3 = Frame(self.f,background='skyblue')
        Label(f3,text='Pieces :').pack(side='left')
        Entry(f3,textvariable=piece).pack()
        f3.pack()

        Button(self.f,text="Inserer",command=ret).pack(side='bottom',padx=4,pady=4)

    def delete(self): # je dois implementer la confirmation
        try:
            id_ = self.tab.selection()[0]
            api = API(setting.get('url'),'arrivages',cookie=temp_setting.cookie)
            api.delete(id_)
        except IndexError:
            pass
        except Exception as e:
            alert_wn(e)
        else:
            self.tab.delete(id_)
            self.temp_index.remove(id_)

class Promotion:
    def __init__(self):
        self.produits = {}
        self.data = {}
        self.window = Toplevel(background='skyblue')
        self.window.title('promotion')
        self.window.resizable(False,False)

        Label(self.window,text="Promotions",font=('',15)).pack(padx=5,pady=5)

        f1 = Frame(self.window,background='skyblue')
        self.tab = ttk.Treeview(f1,columns=['id','occasion','produits','reduction','fin'])

        self.tab.heading('id',text='ID')
        self.tab.heading('occasion',text='Occasion')
        self.tab.heading('produits',text='Produits')
        self.tab.heading('reduction',text='reduction')
        self.tab.heading('fin',text='Fin')
        
        self.tab['show'] = 'headings'

        sc=Scrollbar(f1,command=self.tab.yview)
        sc.pack(side="right",fill='y')

        
        self.tab.configure(yscrollcommand=sc.set)
        self.tab.pack(fill=Y,expand=4)

        f1.pack()

        f2 = Frame(self.window,padx=5,pady=5,background='skyblue')
        Button(f2,text=" Ajouter ",command=self.add,padx=3,pady=3).pack(side='left')
        Button(f2,text=" Voir ",command=self.see,padx=3,pady=3).pack(side='left')
        Button(f2,text=" Supprimmer ",command=self.delete,padx=3,pady=3).pack(side='right')
        f2.pack(side='bottom')

        try:
            api = API(setting.get('url'),'promotions',cookie=temp_setting.cookie)
            data = api.all()

            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            dt = api.all()
            self.produits.update(dt)
        except Exception as e:
            alert_wn(e)
        else:
            self.data.update(data)

            for i , d in data.items():
                p = (
                    d.get('promotion_id'), d.get('label'),
                    ' || '.join(d.get('produits_label')),d.get('reduction'), d.get('date_fin')
                )
                self.tab.insert('','end',iid=d.get('promotion_id'),values=p)
    
    def add(self):
        t_data = {}
        p_labels = []

        def add():
            def insert():
                d = l.curselection()
                n = l.get(d[0])
                id_ = t_data.get(n)
                if not id_ in p_id_list:
                    p_id_list.append(id_)
                    p_labels.append(n)
                    p_list.insert(id_,n)

            def update(data):
                l.delete(0,END)

                for value, i in data.items():
                    l.insert(i,value)

                t_data.clear()
                t_data.update(data)

            def check(f):
                march = add_entry.get()
                if not march:
                    return
        
                if march == '':
                    data = self.produits
                else:
                    data = {}
                for i, d in self.produits.items():
                    n = d.get('label')
                    if march.lower() in n.lower():
                        data[d.get('label')] = d.get('produit_id')

                update(data)


            w = Toplevel(win,background='skyblue')
            w.title('Selection')
            w.resizable(False,False)

            Label(w,text='Selectionner le poduit ',font=('',13),pady=5,padx=5).pack()

            f1 = Frame(w,background='skyblue')
            Label(f1,text='Produit : ').pack(side='left')
            e = Entry(f1,textvariable=add_entry)
            e.bind('<KeyRelease>',check)
            e.pack(side='right')
            f1.pack()

            l = Listbox(w)
            l.pack()

            Button(w,text='Inserer',padx=5,pady=5,command=insert).pack()

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
                win.destroy()
                self.data.update({str(data.get('promotion_id')):data})

                p = (
                    data.get('promotion_id'),
                    data.get('label'),
                    data.get('produits_label'),
                    data.get('reduction'),
                    data.get('date_fin'))
                
                self.tab.insert('','end',iid=data.get('promotion_id'),values=p)

        win = Toplevel(class_="Ajout",padx=10,pady=10,background='skyblue')
        win.resizable(False,False)
        p_id_list = []

        add_entry = StringVar()

        name = StringVar()
        reduction = IntVar(value=0)
        date_f = StringVar()
        date_d = StringVar()

        
        f1 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f1,text="Nom : ").pack(side='left')
        Entry(f1,textvariable=name).pack(side='right')
        f1.pack()

        f1 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f1,text="Reduction (%): ").pack(side='left')
        Entry(f1,textvariable=reduction).pack(side='right')
        f1.pack()

        f1 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f1,text="Debut : ").pack(side='left')
        Entry(f1,textvariable=date_d).pack(side='right')
        f1.pack()

        f2 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f2,text="Fin : ").pack(side='left')
        Entry(f2,textvariable=date_f).pack(side='right')
        f2.pack()

        f3 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f3,text="Produits : ").pack(side='left')
        p_list = Listbox(f3,height=8,width=15)
        p_list.pack(side='left')
        Button(f3,padx=5,pady=5,text='Ajouter',command=add).pack()
        f3.pack()

        f5 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f5,text="Descripton : ").pack(side='left')
        desc = Text(f5,width=15,height=8)
        desc.pack(side='right')
        f5.pack()

        Button(win,text="Enregistrer",command=ret,font=('',15)).pack(side='bottom')

    def delete(self): # je dois implementer la confirmation
        try:
            id_ = self.tab.selection()[0]
            api = API(setting.get('url'),setting.get('url'),'promotions',cookie=temp_setting.cookie)
            api.delete(id_)
        except IndexError:
            pass
        except Exception as e:
            alert_wn(e)
        else:
            self.tab.delete(id_)

    def see(self):
        try:
            id_ = self.tab.selection()[0]
            data = self.data.get(id_)
        except IndexError:
            alert_wn("Veillez d'abord selectionner le client ")
            return
        except Exception as e:
            alert_wn(e)
            return
        

        win = Toplevel(padx=10,pady=10,background='skyblue')
        win.resizable(False,False)

        name = StringVar(value=data.get('label'))
        reduction = IntVar(value=data.get('reduction'))
        l_produits = Variable(value=data.get('produit_id'))
        date_f = StringVar(value=data.get('date_fin'))
        date_d = StringVar(value=data.get('date_depart'))

        f1 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f1,text="Nom : ").pack(side='left')
        Entry(f1,textvariable=name,state='readonly').pack(side='right')
        f1.pack()

        f1 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f1,text="Reduction : ").pack(side='left')
        Entry(f1,textvariable=reduction,state='readonly').pack(side='right')
        f1.pack()

        f1 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f1,text="Debut : ").pack(side='left')
        Entry(f1,textvariable=date_d,state='readonly').pack(side='right')
        f1.pack()

        f2 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f2,text="Fin : ").pack(side='left')
        Entry(f2,textvariable=date_f,state='readonly').pack(side='right')
        f2.pack()

        f3 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f3,text="Produits : ").pack(side='left')
        p_list = Listbox(f3,height=8,width=15)
        p_list.pack(side='left')
        f3.pack()

        for i in data.get('produits_ids'):
            n = self.produits.get(str(i))
            p_list.insert(i,n.get('label'))

        f5 = Frame(win,padx=5,pady=5,background='skyblue')
        Label(f5,text="Descripton : ").pack(side='left')
        desc = Text(f5,height=8,width=15,state='disabled')
        desc.insert('end-1c',data.get('description'))
        desc.pack(side='right')
        f5.pack()

