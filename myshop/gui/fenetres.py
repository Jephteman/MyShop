import time 
from .utils import * 
from .admin_windows import *
from .gestion import *
from tkinter import *
from tkinter import ttk

class win_client:
    def __init__(self):
        self.data = {}
        self.temp_index = []
        self.window = Toplevel(class_='clients',background='skyblue')
        self.window.resizable(False,False)

        self.window.bind('<Control-f>',self.search)
        self.window.bind('<Control-F>',self.search)

        Label(self.window,text="Clients",font=('',15)).pack(padx=5,pady=5)

        f1 = Frame(self.window,background='skyblue')
        self.tab = ttk.Treeview(f1,columns=['id','noms','point','addr','type','tel'])

        self.tab.heading('id',text='ID client')
        self.tab.heading('noms',text='Nom complet')
        self.tab.heading('point',text='Points Bonus')
        self.tab.heading('addr',text='Adresse')
        self.tab.heading('type',text='Type')
        self.tab.heading('tel',text='telephone')
        
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
            api = client.API(setting.get('url'),'clients',cookie=temp_setting.cookie)
            self.data.update(api.all())
        except Exception as e:
            alert_wn(e)
        else:
            for i , d in self.data.items():
                p = (
                    d.get('client_id'),d.get('noms'),d.get('point'),d.get('addr'),
                    'Detaillant' if d.get('type') == 'D' else 'Grossiste',
                    d.get('telephone')
                )
                self.tab.insert('','end',iid=d.get('client_id'),values=p)
                self.temp_index.append(d.get('client_id'))

    def add(self):
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
                api = client.API(setting.get('url'),'clients',cookie=temp_setting.cookie)
                data = api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                win.destroy()
                
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
                self.tab.insert('','end',iid=i_,values=p)
                self.temp_index.append(i_)

        win = Toplevel(class_="Ajout",padx=10,pady=10,background='skyblue')
        win.resizable(False,False)

        noms = StringVar()
        addr = StringVar()
        tel = StringVar()
        sexe = StringVar()
        type_ = StringVar()
        mail = StringVar()
        r_client = StringVar()

        f1 = Frame(win,padx=15,pady=15,background='skyblue')
        Label(f1,text="Noms : ",padx=8,font=('',15)).pack(side='left')
        Entry(f1,textvariable=noms).pack(side='right')
        f1.pack()

        f1 = Frame(win,padx=15,pady=15,background='skyblue')
        Label(f1,text="Sexe : ",padx=8,font=('',15)).pack(side='left')
        ttk.Combobox(f1,textvariable=sexe,values=['M','F'],validate='focusin').pack(side='right')
        f1.pack()

        f1 = Frame(win,padx=15,pady=15,background='skyblue')
        Label(f1,text="Type : ",padx=8,font=('',15)).pack(side='left')
        ttk.Combobox(f1,textvariable=type_,values=['Detaillant','Grossiste'],validate='focusin').pack(side='right')
        f1.pack()

        f2 = Frame(win,padx=15,pady=15,background='skyblue')
        Label(f2,text="Adresse : ",padx=8,font=('',15)).pack(side='left')
        Entry(f2,textvariable=addr).pack(side='right')
        f2.pack()

        f3 = Frame(win,padx=15,pady=15,background='skyblue')
        Label(f3,text="Code parrain : ",padx=8,font=('',15)).pack(side='left')
        Entry(f3,textvariable=r_client).pack(side='right')
        f3.pack()

        f5 = Frame(win,padx=15,pady=15,background='skyblue')
        Label(f5,text="Telephone : ",padx=8,font=('',15)).pack(side='left')
        Entry(f5,textvariable=tel).pack(side='right')
        f5.pack()

        f6 = Frame(win,padx=15,pady=15,background='skyblue')
        Label(f6,text="Email : ",padx=8,font=('',15)).pack(side='left')
        Entry(f6,textvariable=mail).pack(side='right')
        f6.pack()

        Button(win,text="Enregistrer",command=ret,font=('',15)).pack(side='bottom')

    def delete(self): # je dois implementer la confirmation
        try:
            id_ = self.tab.selection()[0]
            api = client.API(setting.get('url'),'clients',cookie=temp_setting.cookie)
            api.delete(id_)
        except IndexError:
            pass
        except Exception as e:
            alert_wn(e)
        else:
            self.tab.delete(id_)
            self.temp_index.remove(id_)

    def see(self):
        def ret():
            param = {
                'client_id':id_,
                'noms':noms.get(),
                'addr':addr.get(),
                'sexe': sexe.get(),
                'type':type_.get()[0],
                'telephone':tel.get(),
                'point':point.get(),
                'email':mail.get(),
            }

            try:
                api = client.API(setting.get('url'),'clients',cookie=temp_setting.cookie)
                data = api.change(param)
            except InterruptedError as e:
                alert_wn(e)
            else:
                win.destroy()
                self.tab.delete(id_)
                self.data.update({data.get('client_id'):data})

                self.tab.insert('','end',iid=id_,values=(
                    data.get('client_id'),
                    data.get('noms'),
                    data.get('point'),
                    data.get('addr'),
                    'Detaillant' if data.get('type') == 'D' else 'Grossiste',
                    data.get('telephone')
                ))

        try:
            id_ = self.tab.selection()[0]
            data = self.data.get(id_)
        except IndexError:
            alert_wn("Veillez d'abord selectionner le client ")
        except InterruptedError as e:
            alert_wn(e)
        else:
            
            win = Toplevel(class_="Ajout",padx=10,pady=10,background='skyblue')
            win.resizable(False,False)

            noms = StringVar(value=data.get('noms'))
            addr = StringVar(value=data.get('addr'))
            tel = StringVar(value=data.get('telephone'))
            sexe = StringVar(value=data.get('sexe'))
            type_ = StringVar(value=data.get('type'))
            mail = StringVar(value=data.get('email'))
            point = IntVar(value=data.get('point'))

            f1 = Frame(win,padx=15,pady=15,background='skyblue')
            Label(f1,text="Noms : ",padx=8,font=('',15)).pack(side='left')
            Entry(f1,textvariable=noms).pack(side='right')
            f1.pack()

            f1 = Frame(win,padx=15,pady=15,background='skyblue')
            Label(f1,text="Sexe : ",padx=8,font=('',15)).pack(side='left')
            ttk.Combobox(f1,textvariable=sexe,values=['M','F'],validate='focusin').pack(side='right')
            f1.pack()

            f1 = Frame(win,padx=15,pady=15,background='skyblue')
            Label(f1,text="Type : ",padx=8,font=('',15)).pack(side='left')
            ttk.Combobox(f1,textvariable=type_,values=['Detaillant','Grossiste'],validate='focusin').pack(side='right')
            f1.pack()

            f1 = Frame(win,padx=15,pady=15,background='skyblue')
            Label(f1,text="Point : ",padx=8,font=('',15)).pack(side='left')
            Entry(f1,textvariable=point).pack(side='right')
            f1.pack()

            f2 = Frame(win,padx=15,pady=15,background='skyblue')
            Label(f2,text="Adresse : ",padx=8,font=('',15)).pack(side='left')
            Entry(f2,textvariable=addr).pack(side='right')
            f2.pack()

            f5 = Frame(win,padx=15,pady=15,background='skyblue')
            Label(f5,text="Telephone : ",padx=8,font=('',15)).pack(side='left')
            Entry(f5,textvariable=tel).pack(side='right')
            f5.pack()

            f6 = Frame(win,padx=15,pady=15,background='skyblue')
            Label(f6,text="Email : ",padx=8,font=('',15)).pack(side='left')
            Entry(f6,textvariable=mail).pack(side='right')
            f6.pack()

            Button(win,text="Enregistrer",command=ret,font=('',15)).pack(side='bottom')

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
                cli = client.API(setting.get('url'),'clients',cookie=temp_setting.cookie).all(param=param)
            except Exception as e:
                alert_wn(e)
                return

            for n in self.temp_index:
                self.tab.delete(n)

            self.temp_index.clear()
            
            for i , d in cli.items():
                p = (
                    d.get('client_id'),d.get('noms'),d.get('point'),d.get('addr'),
                    'Detaillant' if d.get('type') == 'D' else 'Grossiste',
                    d.get('telephone')
                )
                self.tab.insert('','end',iid=d.get('client_id'),values=p)
                self.temp_index.append(d.get('client_id'))

        window = Toplevel(background='skyblue')
        window.resizable(False,False)
        nom = StringVar()
        t = StringVar()
        ref_c = StringVar()
        tel = StringVar()
        addr = StringVar()

        Label(window,text="Recherche Client",font=('',15)).pack()

        f1 = Frame(window,background='skyblue')
        Label(f1,text="Noms : ").pack(side='left')
        Entry(f1,textvariable=nom).pack(side='right')
        f1.pack()

        f2 = Frame(window,background='skyblue')
        Label(f2,text="Type : ").pack(side='left')
        ttk.Combobox(f2,textvariable=t,values=['G','D']).pack(side='right')
        f2.pack()

        f3 = Frame(window,background='skyblue')
        Label(f3,text="Parrain id : ").pack(side='left')
        Entry(f3,textvariable=ref_c).pack(side='right')
        f3.pack()

        f4 = Frame(window,background='skyblue')
        Label(f4,text="Telephone : ").pack(side='left')
        Entry(f4,textvariable=tel).pack(side='right')
        f4.pack()

        f5 = Frame(window,background='skyblue')
        Label(f5,text="Adresse : ").pack(side='left')
        Entry(f5,textvariable=addr).pack(side='right')
        f5.pack()


        Button(window,text="Chercher",command=filtre).pack(padx=5,pady=5)

class mainframe():
    def __init__(self,root):
        self.data = {}
        self.ventes = {}
        self.promotions = {}
        self.n_id = {}
        self.client_id = StringVar()
        self.tmp_march = {}
        self.price = {}

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
        self.var_vendor = temp_setting.get('username')
        self.var_t_prix = StringVar()

        self.error = StringVar()

        ## en-tete qui contient la barre de menu 
        menuBar = Menu(self.root) # ma barred de menu

        #       menu option
        menu_option = Menu(menuBar,tearoff=0)
        menu_option.add_command(label="A propos",command=about)
        menu_option.add_command(label="Exporter ",command=Exporte)
        menu_option.add_command(label="Parametre *",command=Parametre) 
        menu_option.add_command(label="Quitter",command=self.root.destroy)
        menuBar.add_cascade(menu=menu_option,label="Options")
        
        #       menu gestion
        menu_gestion = Menu(menuBar,tearoff=0)
        menu_gestion.add_command(label="Inventaire",command=inventaire) 
        menu_gestion.add_command(label="Arrivage",command=arrivage)
        menu_gestion.add_command(label="Stock",command=stock)
        menu_gestion.add_command(label="Clients",command=win_client)
        menu_gestion.add_command(label="Actualiser",command=self.actualiser)
        menuBar.add_cascade(menu=menu_gestion,label="Gestion")

        #       menu  administrationmenu_outils
        menu_admin = Menu(menuBar,tearoff=0)
        menu_admin.add_command(label="Utilisateurs ",command=users_admin)
        menu_admin.add_command(label="Promotion ",command=Promotion)
        menu_admin.add_command(label="Sessions ",command=session_admin)
        menu_admin.add_command(label="Monitoring ",command=monitoring)
        menuBar.add_cascade(menu=menu_admin,label="Administration") 

        #       menu  outils
        menu_outils = Menu(menuBar,tearoff=0)
        menu_outils.add_command(label="Graphique",command=Graphique) 
        menu_outils.add_command(label="Notes",command=Notes)
        menuBar.add_cascade(menu=menu_outils,label="Outils")
        
        self.root.config(menu=menuBar)

        ##      corps de la page 
        body = Frame(self.root,background='skyblue')

        # le frame de gauche qui contient la liste
        f_left = Frame(body,width=20,padx=15,pady=15,background='skyblue')

        
        f4 = Frame(f_left,background='skyblue')
        Label(f4,text="Date :",border='5').pack(side='left')
        Label(f4,textvariable=self.var_date).pack(side='right')
        f4.pack()

        f5 = Frame(f_left,background='skyblue')
        Label(f5,text="Nom du vendeur  :",border='5').pack(side='left')
        Label(f5,text=self.var_vendor).pack(side='right')
        f5.pack()

        f6 = Frame(f_left,background='skyblue')
        Label(f6,text="Id du client  :",border='5').pack(side='left')
        Entry(f6,textvariable=self.client_id).pack(side='left')
        f6.pack()

        f7 = Frame(f_left,background='skyblue')
        Label(f7,text="Marchandises :",border='5').pack(side='left')
        f7.pack()

        f8 = Frame(f_left,height=90,width=135,background='skyblue')
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

        f9 = Frame(f_left,border=5,background='skyblue')
        Label(f9,text='Total :').pack(side='left')
        Label(f9,textvariable=self.var_t_prix).pack(side='right')
        f9.pack()
        
        f10_ = Frame(f_left,border=4,background='skyblue')
        Label(f10_,text="Produit : ").pack(side='left')
        self.entry = Entry(f10_)
        self.entry.pack(side='right')
        self.entry.bind('<KeyRelease>',self.check)
        f10_.pack()

        f10 = Frame(f_left,border=4,background='skyblue')
        self.l_march = Listbox(f10,height=10,width=25)
        self.l_march.pack(side='left')
        Entry(f10,textvariable=self.var_piece,width=10).pack(side='left')
        Button(f10,text='Valider',command=self.insert_tab).pack(side='right')
        f10.pack()
        
        f11 = Frame(f_left,border=3,background='skyblue')
        Button(f11,text="Nouveau",command=self.nouv_fonc).pack(side='left')
        Button(f11,text="Annuler",command=self.anul_fonc).pack(side='left')
        Button(f11,text="Sauvegarder",command=self.sauv_fonc).pack(side='right')
        f11.pack(side='bottom')
        
        f_left.pack(fill=Y,side='left',padx=5,pady=5)

        # frame de droite 
        f_right = Frame(self.root,padx=10,pady=10,background='skyblue')

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
        self.lc.bind('<Double-Button-1>',self.print)


        sc=Scrollbar(f_right,command=self.lc.yview)
        sc.pack(side="right",fill='y')

        self.lc.pack(fill=Y,expand=4)
        self.lc.configure(yscrollcommand=sc.set)
        
        
        f_right.pack(fill='both',side=RIGHT,expand=1)
        body.pack()

        self.actualiser()

        self.root.mainloop()

    def actualiser(self):
        try:
            self.promotions = client.API(setting.get('url'),'promotions',cookie=temp_setting.cookie).all({'valide':True})
            api = client.API(setting.get('url'),'produits',cookie=temp_setting.cookie)
            data = api.all()
        except InterruptedError as e:
            alert_wn(e)
        else:
            self.data.clear()
            self.data.update(data)
            for i , d in self.data.items():
                self.n_id.update({d.get('label'):i})
    
    def sauv_fonc(self):
        if not self.tmp_march:
            return 
        
        param = {"client_id":self.client_id.get()}
        param['marchandises'] = {}

        str_march = ''

        for p_id , qprod_idtab in self.tmp_march.items():
            p_id = str(p_id)
            n_produit = self.data.get(p_id).get('label')
            param['marchandises'].update({p_id:qprod_idtab['quantite']})
            str_march += f"{n_produit} ({qprod_idtab['quantite']}) || "

        try:
            api = client.API(setting.get('url'),'ventes',cookie=temp_setting.cookie)
            data = api.add(param)
        except Exception as e:
            alert_wn(e)
        else :
            i_ = data.get('vente_id')
            self.ventes.update({i_:data})
             
            self.lc.insert('',i_,iid=i_,values=[
                data.get('client_id'),
                self.var_vendor,
                str_march[:-3],
                data.get('prix'),
                data.get('date')
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

        for i in self.tmp_march.keys():
            self.lc_temp.delete(i)

        self.var_marchandise.set('')
        self.var_piece.set('1')
        self.var_prix.set('')
        self.tmp_march.clear()

    def insert_tab(self):
        march = self.l_march.curselection()
        reduction = 0

        if not march:
            return
        
        march = self.l_march.get(march[0])
        march = self.n_id.get(march)
        march = self.data.get(march)

        if not march.get('produit_id'):
            alert_wn(f"Le produit '{march}' n'existe pas dans la base de donnée")
            return
        
        for prom_id, prom_info in self.promotions.items(): # nous verifions si le produits a une quelconque promotion en cours
            if int(march.get('produit_id')) in prom_info.get('produits_ids'):
                reduction += prom_info.get('reduction')
        
        
        quatite = self.var_piece.get()
        p_id = march.get('produit_id')

        if self.lc_temp.exists(p_id):
            pr, dev = march.get('prix').split(sep=' ')
            pr = int(pr)
            pr -= (reduction*pr)//100

            self.tmp_march[p_id]['quantite'] += quatite
            self.tmp_march[p_id]['prix'] = f"{pr * self.tmp_march[p_id]['quantite']} {dev}"
            self.lc_temp.delete(p_id)
            self.lc_temp.insert('','end',iid=p_id,values=(march.get('label'),self.tmp_march[p_id]['quantite'],self.tmp_march[p_id]['prix']))
        
        else:
            self.tmp_march[p_id] = {'quantite':0,'prix':''}
            pr, dev = march.get('prix').split(sep=' ')
            pr = int(pr)
            pr -= (reduction*pr)//100 
            prix = f'{pr * quatite} {dev}'

            self.tmp_march[p_id]['quantite'] = quatite
            self.tmp_march[p_id]['prix'] = prix

            self.lc_temp.insert('','end',iid=p_id,values=(march.get('label'),quatite,prix))

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

        self.var_t_prix.set(str_price[1:])

    def del_temp(self,event):
        """suprimme un element dans la liste temp"""
        try:
            item = self.lc_temp.selection()[0]
            self.lc_temp.delete(item)
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

            self.var_t_prix.set(str_price)

    def print(self,event):
        try:
            id_ = self.lc.selection()[0]
            data = self.ventes.get(int(id_))
        except IndexError:
            alert_wn("Veillez d'abord selectionner")
        else:
            Printer(data)

    def check(self,e):
        march = self.entry.get()
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
        self.l_march.delete(0,END)
        for i, value in data.items():
            self.l_march.insert(i,value)


