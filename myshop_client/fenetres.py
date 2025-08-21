import time 
from .utils import alert_wn, API, setting, temp_setting, clean_variable, Printer
from tkinter import *
from .widgets import *

class ClientPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.data = {}
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
        
    def show_frame(self, cont,action=''):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        clean_variable(frame)
        if cont != 'Home' and action:
            tab = self.frames['Home'].nametowidget('body.tableau')
            id_ = tab.selection()[0]
            data = self.data.get(id_)
            
            frame.setvar('var_noms',data.get('noms'))
            frame.setvar('var_addr',data.get('addr'))
            frame.setvar('var_tel',data.get('telephone'))
            frame.setvar('var_sexe',data.get('sexe'))
            frame.setvar('var_type',data.get('type'))
            frame.setvar('var_email',data.get('email'))
            frame.setvar('var_r_client',data.get('r_client'))
            
        frame.tkraise()
        
    def actualise(self):
        try:
            api = API(setting.get('url'),'clients',cookie=temp_setting.cookie)
            self.data.update(api.all())
        except Exception as e:
            alert_wn(e)
        
        tab = self.frames['Home'].nametowidget('body.tableau')
        
        for i , d in self.data.items():
            p = (
                d.get('client_id'),d.get('noms'),d.get('point'),d.get('addr'),
                'Detaillant' if d.get('type') == 'D' else 'Grossiste',
                d.get('telephone')
            )
            if not tab.exists(int(i)):
                tab.insert('','end',iid=d.get('client_id'),values=p)
                self.temp_index.append(d.get('client_id'))
        
    def Home(self,container):
        frame  = Frame(container,name='frame_home',background='skyblue')

        frame.bind('<Control-f>',self.search)
        frame.bind('<Control-F>',self.search)

        Label(frame,text="Clients",font=('',15),background='skyblue').pack(padx=5,pady=5)
        
        f1 = Frame(frame,background='skyblue',name='body')
        tab = ttk.Treeview(f1,columns=('id','noms','point','addr','type','tel'),name='tableau')

        tab.heading('id',text='ID client')
        tab.heading('noms',text='Nom complet')
        tab.heading('point',text='Points Bonus')
        tab.heading('addr',text='Adresse')
        tab.heading('type',text='Type')
        tab.heading('tel',text='telephone')
        
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
        def ret():
            param = {
                'noms':noms.get(),
                'addr':addr.get(),
                'sexe': sexe.get()[0],
                'type':type_.get()[0],
                'refer_client':r_client.get(),
                'telephone':tel.get(),
                'email':mail.get(),
                'isform':True
            }
            if tel.get() :
                param['client_id'] = tel.get()

            try:
                api = API(setting.get('url'),'clients',cookie=temp_setting.cookie)
                data = api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                self.show_frame('Home')
                tab = self.frames['Home'].nametowidget('body.tableau')
                
                i_ = str(data.get('client_id'))
                self.data.update({i_:data})
                p = (
                    i_,
                    data.get('noms'),
                    data.get('point'),
                    data.get('addr'),
                    'Detaillant' if data.get('type') == 'D' else 'Grossiste',
                    data.get('telephone')
                )
                tab.insert('','end',iid=i_,values=p)
                self.temp_index.append(i_)
        
        frame = Frame(container,name='frame_add',background='skyblue')
        Label(frame,text="Insertion d'un client",padx=15,pady=15,font=('',15),background='skyblue').pack()
        noms = StringVar(frame,name='var_noms')
        addr = StringVar(frame,name='var_addr')
        tel = StringVar(frame,name='var_tel')
        sexe = StringVar(frame,name='var_sexe')
        type_ = StringVar(frame,name='var_type')
        mail = StringVar(frame,name='var_mail')
        r_client = StringVar(frame,name='var_r_client')

        PlaceholderEntry(frame,textvariable=noms,placeholder="Nom du client").pack()
        PlaceholderEntry(frame,textvariable=tel,placeholder="Numero de telephone").pack()
        PlaceholderEntry(frame,textvariable=r_client,placeholder="Code du parrain (facultatif)").pack()
        PlaceholderEntry(frame,textvariable=addr,placeholder='Addresse ').pack()
        PlaceholderEntry(frame,textvariable=mail,placeholder="Adresse mail").pack()
        
        f1 = Frame(frame,padx=15,pady=15,background='skyblue')
        Label(f1,text="Sexe : ",padx=8,font=('',15),background='skyblue').pack(side='left')
        ttk.Combobox(f1,textvariable=sexe,values=['M','F'],validate='focusin').pack(side='right')
        f1.pack()

        f1 = Frame(frame,padx=15,pady=15,background='skyblue')
        Label(f1,text="Type : ",padx=8,font=('',15),background='skyblue').pack(side='left')
        ttk.Combobox(f1,textvariable=type_,values=['Detaillant','Grossiste'],validate='focusin').pack(side='right')
        f1.pack()
        
        f7 = Frame(frame,padx=15,pady=15,background='skyblue')
        Button(f7,text="Enregistrer",command=ret,font=('',15)).pack(side='left')
        Button(f7,text="Annuler",command=lambda : self.show_frame('Home'),font=('',15)).pack(side='right')
        f7.pack(side='bottom')
        
        return frame

    def delete(self): # je dois implementer la confirmation
        try:
            tab = self.frames['Home'].nametowidget('body.tableau')
            id_ = tab.selection()[0]
            api = API(setting.get('url'),'clients',cookie=temp_setting.cookie)
            api.delete(id_)
        except IndexError:
            pass
        except Exception as e:
            alert_wn(e)
        else:
            tab.delete(id_)
            self.temp_index.remove(id_)

    def search(self,event):
        def filtre():
            try:
                param = {
                    'noms':nom.get(),
                    'type':t.get(),
                    'refer_client':ref_c.get(),
                    'addr':addr.get(),
                    'telephone':tel.get()
                }
                cli = API(setting.get('url'),'clients',cookie=temp_setting.cookie).all(param=param)
            except Exception as e:
                alert_wn(e)
                return
                
            tab = self.frames['Home'].nametowidget('body.tableau')
            for n in self.temp_index:
                tab.delete(n)

            self.temp_index.clear()
            
            for i , d in cli.items():
                p = (
                    d.get('client_id'),d.get('noms'),d.get('point'),d.get('addr'),
                    'Detaillant' if d.get('type') == 'D' else 'Grossiste',
                    d.get('telephone')
                )
                tab.insert('','end',iid=d.get('client_id'),values=p)
                self.temp_index.append(d.get('client_id'))

        window = Toplevel(background='skyblue')
        window.resizable(False,False)
        nom = StringVar()
        t = StringVar()
        ref_c = StringVar()
        tel = StringVar()
        addr = StringVar()

        Label(window,text="Recherche Client",font=('',15),background='skyblue').pack()

        f1 = Frame(window,background='skyblue')
        Label(f1,text="Noms : ",background='skyblue').pack(side='left')
        Entry(f1,textvariable=nom).pack(side='right')
        f1.pack()

        f2 = Frame(window,background='skyblue')
        Label(f2,text="Type : ",background='skyblue').pack(side='left')
        ttk.Combobox(f2,textvariable=t,values=['G','D']).pack(side='right')
        f2.pack()

        f3 = Frame(window,background='skyblue')
        Label(f3,text="Parrain id : ",background='skyblue').pack(side='left')
        Entry(f3,textvariable=ref_c).pack(side='right')
        f3.pack()

        f4 = Frame(window,background='skyblue')
        Label(f4,text="Telephone : ",background='skyblue').pack(side='left')
        Entry(f4,textvariable=tel).pack(side='right')
        f4.pack()

        f5 = Frame(window,background='skyblue')
        Label(f5,text="Adresse : ",background='skyblue').pack(side='left')
        Entry(f5,textvariable=addr).pack(side='right')
        f5.pack()
        
        Button(window,text="Chercher",command=filtre).pack(padx=5,pady=5)

class VentePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.data = {}
        self.ventes = {}
        self.promotions = {}
        self.n_id = {}
        self.tmp_march = {}
        self.price = {}

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        # Création des différentes frames
        for F in (self.Home,):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        # Afficher la première frame
        self.show_frame("Home")
    
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        if cont != 'Home':
            clean_variable(frame)
        frame.tkraise()
            
    def Home(self,container):
        frame = Frame(container,name='frame_home',background='skyblue')
        client_id = StringVar(frame,name='var_client_id')
        
        ## ces variables sont utiliser pour sauvegarder les entrees utilisateur
        var_marchandise = StringVar(frame,name='var_marchandise')
        var_piece = IntVar(frame,name='var_piece',value=1)
        var_prix = StringVar(frame,name='var_prix')
        var_t_prix = StringVar(frame,name='var_t_prix')
       
        # le frame de gauche qui contient la liste
        f_left = Frame(frame,width=20,padx=15,pady=15,background='skyblue',name='frame_gauche')

        f6 = Frame(f_left,background='skyblue')
        Label(f6,text="Id du client  :",border='5',background='skyblue').pack(side='left')
        PlaceholderEntry(f6,textvariable=client_id,placeholder="ex : 0991374833").pack(side='left')
        f6.pack()

        f7 = Frame(f_left,background='skyblue')
        Label(f7,text="Marchandises :",border='5',background='skyblue').pack(side='left')
        f7.pack()

        f8 = Frame(f_left,height=90,width=135,background='skyblue',name='frame_tableau_panier')
        lc_temp = ttk.Treeview(f8,columns=('produit','quantite','prix'),name='tableau_panier')#,height=50)
        lc_temp.heading('produit',text='Produits')
        lc_temp.column('produit',width=80)
        lc_temp.heading('quantite',text='Quantite')
        lc_temp.column('quantite',width=60)
        lc_temp.heading('prix',text='Prix')
        lc_temp.column('prix',width=80)
        lc_temp['show'] = 'headings'
        lc_temp.bind('<Control-D>',self.del_temp)
        lc_temp.bind('<Control-d>',self.del_temp)

        lc_temp.pack(fill=Y,expand=1)
        f8.pack()

        f9 = Frame(f_left,border=5,background='skyblue')
        Label(f9,text='Total :',background='skyblue').pack(side='left')
        Label(f9,textvariable=var_t_prix,background='skyblue').pack(side='right')
        f9.pack()
        
        f10_ = Frame(f_left,border=4,background='skyblue',name='frame_entry')
        Label(f10_,text="Produit : ",background='skyblue').pack(side='left')
        entry = Entry(f10_,name='entry')
        entry.pack(side='right')
        entry.bind('<KeyRelease>',self.check)
        f10_.pack()

        f10 = Frame(f_left,border=4,background='skyblue',name='frame_list')
        l_march = Listbox(f10,height=10,width=25,name='list_march')
        l_march.pack(side='left')
        Entry(f10,textvariable=var_piece,width=10).pack(side='left')
        Button(f10,text='Valider',command=self.insert_tab).pack(side='right')
        f10.pack()
        
        f11 = Frame(f_left,border=3,background='skyblue')
        Button(f11,text="Nouveau",command=self.annul_fonc).pack(side='left')
        Button(f11,text="Sauvegarder",command=self.sauv_fonc).pack(side='right')
        f11.pack(side='bottom')
        
        f_left.pack(fill=Y,side='left',padx=5,pady=5)

        # frame de droite 
        f_right = Frame(frame,padx=10,pady=10,background='skyblue',name='frame_droit')

        lc = ttk.Treeview(f_right,columns=('name','vendor','produit','prix','date'),name='tableau_fact')
        lc.heading('name',text='Id client')
        lc.heading('vendor',text='Vendeur')
        lc.column('vendor',width=125)
        lc.heading('produit',text='Produit')
        lc.heading('prix',text='Prix')
        lc.column('prix',width=75)
        lc.heading('date',text='Date')
        lc.column('date',width=175)
        lc['show'] = 'headings'
        lc.bind('<Double-Button-1>',self.print)

        sc=Scrollbar(f_right,command=lc.yview)
        sc.pack(side="right",fill='y')

        lc.pack(fill='both',expand=4)
        lc.configure(yscrollcommand=sc.set)
        
        f_right.pack(fill='both',side=RIGHT,expand=1)

        return frame

    def actualise(self):
        try:
            self.promotions = API(setting.get('url'),'promotions',cookie=temp_setting.cookie).all({'valide':True})
            api = API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            data = api.all()
        except Exception as e:
            alert_wn(e)
        else:
            self.data.clear()
            self.data.update(data)
            for i , d in self.data.items():
                self.n_id.update({d.get('label'):i})
    
    def sauv_fonc(self):
        if not self.tmp_march:
            return 
        
        param = {"client_id":self.getvar('var_client_id')}
        param['marchandises'] = {}

        str_march = ''

        for p_id , qprod_idtab in self.tmp_march.items():
            p_id = str(p_id)
            n_produit = self.data.get(p_id).get('label')
            param['marchandises'].update({p_id:qprod_idtab['quantite']})
            str_march += f"{n_produit} ({qprod_idtab['quantite']}) || "
        try:
            api = API(setting.get('url'),'ventes',cookie=temp_setting.cookie)
            data = api.add(param)
        except Exception as e:
            alert_wn(e)
        else :
            i_ = data.get('vente_id')
            self.ventes.update({i_:data})
            
            lc = self.frames['Home'].nametowidget('frame_droit.tableau_fact')
             
            lc.insert('',i_,iid=i_,values=[
                data.get('client_id'),
                temp_setting.get('username'),
                str_march[:-3],
                data.get('prix'),
                data.get('date')
            ])
            self.annul_fonc()

    def annul_fonc(self):
        """anulle le entrees utulisateur"""
        clean_variable(self.frames['Home'])
        self.frames['Home'].setvar('var_piece','1')
        
        lc_temp = self.frames['Home'].nametowidget('frame_gauche.frame_tableau_panier.tableau_panier')

        for i in self.tmp_march.keys():
            lc_temp.delete(i)

        self.tmp_march.clear()     

    def insert_tab(self):
        l_march = self.frames['Home'].nametowidget('frame_gauche.frame_list.list_march')
        lc_temp = self.frames['Home'].nametowidget('frame_gauche.frame_tableau_panier.tableau_panier')
        
        march = l_march.curselection()
        reduction = 0

        if not march:
            return
        
        march = l_march.get(march[0])
        march = self.n_id.get(march)
        march = self.data.get(march)

        if not march.get('produit_id'):
            alert_wn(f"Le produit '{march}' n'existe pas dans la base de donnée")
            return
        
        for prom_id, prom_info in self.promotions.items(): # nous verifions si le produits a une quelconque promotion en cours
            if int(march.get('produit_id')) in prom_info.get('produits_ids'):
                reduction += prom_info.get('reduction')
        
        quatite = self.frames['Home'].getvar('var_piece')
        p_id = march.get('produit_id')

        if lc_temp.exists(p_id):
            pr, dev = march.get('prix').split(sep=' ')
            pr = int(pr)
            pr -= (reduction*pr)//100

            self.tmp_march[p_id]['quantite'] += int(quatite)
            
            pr = pr * int(self.tmp_march[p_id]['quantite'])
            
            self.tmp_march[p_id]['prix'] = f"{pr} {dev}"
            lc_temp.delete(p_id)
            lc_temp.insert('','end',iid=p_id,values=(march.get('label'),self.tmp_march[p_id]['quantite'],self.tmp_march[p_id]['prix']))
        else:
            self.tmp_march[p_id] = {'quantite':0,'prix':''}
            pr, dev = march.get('prix').split(sep=' ')
            pr = int(pr)
            pr -= (reduction*pr)//100 
            pr = pr * int(quatite)
            prix = f'{pr} {dev}'

            self.tmp_march[p_id]['quantite'] = int(quatite)
            self.tmp_march[p_id]['prix'] = prix

            lc_temp.insert('','end',iid=p_id,values=(march.get('label'),quatite,prix))

        t = {}
        
        for id_ , d in self.tmp_march.items(): # nous faisons la sommes des prix en espectant les devices
            pr , dev = d['prix'].split(sep=' ')
            if dev in t :
                t[dev] += int(pr)
            else:
                t[dev] = int(pr)

        self.price.update(t)
        str_price = ''
        for dev , prix in self.price.items():
            if prix == 0:
                continue
            str_price += f'+ {prix} {dev}'
                        
        self.frames['Home'].setvar('var_t_prix',str_price[1:])

    def del_temp(self,event):
        """suprimme un element dans la liste temp"""
        lc_temp = self.frames['Home'].nametowidget('frame_gauche.frame_tableau_panier.tableau_panier')
        try:
            item = lc_temp.selection()[0]
            lc_temp.delete(item)
        except :
            pass
        else:
            item = int(item)
            prix = self.tmp_march.get(item)['prix']
            chif, dev = prix.split(sep=' ')

            del self.tmp_march[item]

            self.price[dev] -= int(chif)

            str_price = ''
            for dev , prix in self.price.items():
                if prix == 0:
                    continue
                
                str_price += f'+ {prix} {dev}'

            self.frames['Home'].setvar('var_t_prix',str_price)

    def print(self,event):
        lc = self.frames['Home'].nametowidget('frame_droit.tableau_fact')
        try:
            id_ = lc.selection()[0]
            data = self.ventes.get(int(id_))
        except IndexError:
            alert_wn("Veillez d'abord selectionner")
        except Exception as e:
            alert_wn(e)
        else:
            Printer(data)

    def check(self,e):
        entry = self.frames['Home'].nametowidget('frame_gauche.frame_entry.entry')
        march = entry.get()
        if not march:
            return
        
        if march == '':
           data = self.data
        else:
            data = {}
            for i, d in self.data.items():
                n = d.get('label')
                if march.lower() in n.lower():
                    data[d.get('produit_id')] = n

        self.update(data)

    def update(self,data):
        l_march = self.frames['Home'].nametowidget('frame_gauche.frame_list.list_march')
        l_march.delete(0,END)
        
        for i, value in data.items():
            l_march.insert(i,value)


