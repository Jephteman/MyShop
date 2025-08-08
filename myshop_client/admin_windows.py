from .utils import alert_wn, API, setting, temp_setting, clean_variable
from .widgets import *


class UserPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller 
        self.tab_index = {}
        self.data = {}
        
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        
        # Création des différentes frames
        for F in (self.Home, self.Add, self.Change, self.ResetPasswd):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Afficher la première frame
        self.show_frame("Home")
        
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        clean_variable(frame)
        if not cont in [ 'Home', 'Add']:
            tab = self.frames['Home'].nametowidget('body.tableau')
            try:
                login_id = tab.selection()[0]
            except Exception as e:
                alert_wn(e)
                return
                
            if cont == 'Change':
                data = self.data.get(login_id)
            
                frame.setvar('var_uname',data.get('uname'))
                frame.setvar('var_passwd',data.get('*******'))
                frame.setvar('var_addr',data.get('addr'))
                frame.setvar('var_noms',data.get('noms'))
                frame.setvar('var_tel',data.get('telephone'))
                frame.setvar('var_email',data.get('email'))
                #frame.setvar('var_photo',data.get('photo'))
                frame.setvar('var_role',data.get('role'))
                
            if cont == 'ResetPasswd':
                frame.setvar('var_login_id',login_id)
                
        frame.tkraise()
        
    def actualise(self):
        self.data = {}
        try:
            data1 = API(setting.get('url'),'users',cookie=temp_setting.cookie).all()
            data2 = API(setting.get('url'),'agents',cookie=temp_setting.cookie).all()
            for i in data1.keys():
                d = data1.get(i)

                try:
                    d.update(data2.get(i))
                except :
                    continue

                self.data[i] = d
        except Exception as e:
            alert_wn(e)

        else:
            lc = self.frames['Home'].nametowidget('body.tableau')
            for index, info in self.data.items() : 
                if not lc.exists(int(index)):
                    p = (int(index),info.get('username'),info.get('noms'),info.get('role'),'actif' if info.get('statut') else 'bloquer')
                    x = lc.insert('','end',iid=index,values=p )    
        
    def Home(self,container):
        frame = Frame(container,name='frame_home',background='skyblue')

        Label(frame,text="Utilisateurs",font=('',15),background='skyblue').pack(padx=5,pady=5)

        f1 = Frame(frame,padx=10,pady=10,background='skyblue',name='body')
        lc = ttk.Treeview(f1,columns=('id','usernames','noms','role','statut'),name='tableau')
        lc.heading('id',text="Id")
        lc.heading('usernames',text='Usernames')
        lc.heading('noms',text="Noms")
        lc.heading('role',text="Role")
        lc.heading('statut',text="Statut")
        lc['show']='headings'

        sc = Scrollbar(f1,command=lc.yview)
        sc.pack(side="right",fill=Y)

        lc.configure(yscrollcommand=sc.set)

        lc.pack(fill='both',expand=True)

        f1.pack(fill='both',expand=True)

        f_both = Frame(frame,padx=10,pady=10,background='skyblue')
        Button(f_both,text='Ajouter',command=lambda : self.show_frame('Add')).pack(side='left')
        Button(f_both,text='Change',command=lambda : self.show_frame('Change')).pack(side='left')
        Button(f_both,text="Changer le mdp",command=lambda : self.show_frame('ResetPasswd')).pack(side='left')
        Button(f_both,text='Delete',command=self.delete).pack(side='right')

        f_both.pack(side='bottom')
        
        return frame

    def Add(self,container):
        def ret():
            # recupoerer limage et la convertir en base64
            param = {
                'noms':var_noms.get(),
                'username':var_uname.get(),
                'password':var_passwd.get(),
                'addr':var_addr.get(),
                'role':var_role.get(),
                'telephone':var_tel.get(),
                'email':var_email.get(),
                #'photo':''
            }
            #if self.var_photo.get():
            #    photo = open(self.var_photo,'rb').read()
            #    photo = base64.encodebytes(photo)
            #    param['photo'] = photo

            try:
                api = API(setting.get('url'),'users',cookie=temp_setting.cookie)
                data = api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                data.update(param)
                self.data[str(data.get('login_id'))] = data
                lc = self.frames['Home'].nametowidget('body.tableau')
                i_ = str(data.get('login_id'))
                x = lc.insert('','end',iid=i_,values=(
                    i_,data.get('username'),
                    data.get('noms'),data.get('role'),
                    'actif'))
                alert_wn("Le compte a été crée avec success")
                self.show_frame('Home')

        frame = Frame(container,name='frame_add',background='skyblue')
        var_role = StringVar(frame,name='var_role')
        var_uname = StringVar(frame,name='var_uname')
        var_passwd = StringVar(frame,name='var_passwd')
        var_addr = StringVar(frame,name='var_addr')
        var_noms = StringVar(frame,name='var_noms')
        var_tel = StringVar(frame,name='var_tel')
        var_email = StringVar(frame,name='var_email')
        #var_photo = StringVar(frame,name='var_photo')

        Label(frame,text="Création d'un compte",font=('',29),pady=15,background='skyblue').pack()

        f_noms = Frame(frame,background='skyblue')
        #Label(f_noms,text="Noms : ",font=('',15),background='skyblue').pack(side='left')
        PlaceholderEntry(f_noms,textvariable=var_noms,placeholder="Noms").pack()
        f_noms.pack()

        f_uname = Frame(frame,background='skyblue')
        PlaceholderEntry(f_uname,textvariable=var_uname,placeholder="Nom d'utilisateur").pack()
        f_uname.pack()

        f_pass = Frame(frame,background='skyblue')
        PlaceholderEntry(f_pass,textvariable=var_passwd,placeholder="Mot de pass").pack()
        f_pass.pack()

        f_role = Frame(frame,background='skyblue')
        Label(f_role,text="Role : ",font=('',15),background='skyblue').pack(side='left')
        ttk.Combobox(f_role,textvariable=var_role,values=('admin','vendeur','moniteur')).pack(side='right')
        f_role.pack()

        f_addr = Frame(frame,background='skyblue')
        PlaceholderEntry(f_addr,textvariable=var_addr,placeholder="Adresse").pack()
        f_addr.pack()

        f_num = Frame(frame,background='skyblue')
        PlaceholderEntry(f_num,textvariable=var_tel,placeholder="Telephone").pack()
        f_num.pack()

        f_mail = Frame(frame,background='skyblue')
        Label(f_mail,text="Email : ",font=('',15),background='skyblue').pack(side='left')
        Entry(f_mail,textvariable=var_email).pack(side='right')
        f_mail.pack()

        #f_photo = Frame(frame,background='skyblue')
        #Label(f_photo,text="Photo : ",font=('',15),background='skyblue').pack(side='left')
        #Button(f_photo,text='parcourir',command=self.set_file).pack(side='right') #   parcourir nest pas implementer
        #Entry(f_photo,textvariable=var_photo,state='readonly').pack(side='right')
        #f_photo.pack()

        
        f3 = Frame(frame,background='skyblue')
        Button(f3,text="Creer le compte",command=ret,pady=10,width=20).pack(side='left')
        Button(f3,text='Annuler',padx=10,pady=10,width=15,command=lambda: self.show_frame('Home')).pack(side='right')
        f3.pack(padx=10,pady=10)

        
        return frame

    #def set_file(self):
    #    t = [('Image File','*.png'),('Image File','*.jpg')]
    #    askfile_open(self.var_photo,t) ### cette portion de code ne fonctionne pas

    def delete(self):
        def ret():
            try:
                lc = self.frames['Home'].nametowidget('body.tableau')
                i = lc.selection()
                if not i:
                    return
        
                user_id = i[0]
                api = API(setting.get('url'),'users',cookie=temp_setting.cookie)
                api.delete(user_id)
            except Exception as e:
                alert_wn(e)
            else:
                alert_wn('Utilisateur suprimé avec success')
                lc.delete(user_id)
                
        
        """
        frame = Frame(container,name='frame_add',background='skyblue')

        Label(frame,text=f"Voullez-vous supprimer l'utilisateur {self.data[user_id].get('username')} ?",padx=10,font=('',13),).pack()

        f1 = Frame(frame,background='skyblue')
        Button(f1,text="  OUI  ",font=('',9),command=ret,pady=6,width=10).pack(side=LEFT)
        Button(f1,text='  NON  ',command=window.destroy,font=('',9),pady=6,width=10).pack(side=RIGHT)
        f1.pack()
        
        return frame
        """

    def Change(self,container):
        def ret():
            param = {
                'login_id':var_login_id.get(),
                'user_id':var_login_id.get(),
                'noms':var_noms.get(),
                'addr':var_addr.get(),
                'role':var_role.get(),
                'telephone':var_tel.get(),
                'email':var_email.get(),
                #'photo':'' # nous devons avoir une foction qui encode en base64 limage 
            }

            try:
                api = API(setting.get('url'),'users',cookie=temp_setting.cookie)
                api.change(param)
            except Exception as e:
                alert_wn(e)
            else:
                lc = self.frames['Home'].nametowidget('body.tableau')
                i = lc.selection()
                self.show_frame('Home')
                lc.delete(i[0])
                lc.insert(
                    '',i[0],iid=i[0],values=(
                        i[0],api.get('username'),
                        param.get('noms'),param.get('role'),
                        'actif' if api.get('statut') else 'bloquer')
                    )
                
                alert_wn("Le compte a ete modifier avec success")
                self.show_frame('Home')
        
        frame = Frame(container,name='frame_change',background='skyblue')
        var_login_id = StringVar(frame,name='var_login_id')
        var_role = StringVar(frame,name='var_role')
        var_addr = StringVar(frame,name='var_addr')
        var_noms = StringVar(frame,name='var_noms')
        var_tel = StringVar(frame,name='var_tel')
        var_email = StringVar(frame,name='var_email')
        #var_photo = StringVar(frame,name='var_photo')

        Label(frame,text="Modification d'un compte",font=('',29),pady=15,background='skyblue').pack()

        f_noms = Frame(frame,background='skyblue')
        Label(f_noms,text="Noms : ",font=('',15),background='skyblue').pack(side='left')
        Entry(f_noms,textvariable=var_noms).pack(side='right')
        f_noms.pack()

        f_role = Frame(frame,background='skyblue')
        Label(f_role,text="Role : ",font=('',15),background='skyblue').pack(side='left')
        ttk.Combobox(f_role,textvariable=var_role,values=('admin','vendeur','moniteur')).pack(side='right')
        f_role.pack()

        f_addr = Frame(frame,background='skyblue')
        Label(f_addr,text="Addrese : ",font=('',15),background='skyblue').pack(side='left')
        Entry(f_addr,textvariable=var_addr).pack(side='right')
        f_addr.pack()

        f_num = Frame(frame,background='skyblue')
        Label(f_num,text="Numero : ",font=('',15),background='skyblue').pack(side='left')
        Entry(f_num,textvariable=var_tel).pack(side='right')
        f_num.pack()

        f_mail = Frame(frame,background='skyblue')
        Label(f_mail,text="Email : ",font=('',15),background='skyblue').pack(side='left')
        Entry(f_mail,textvariable=var_email).pack(side='right')
        f_mail.pack()

        #f_photo = Frame(frame,background='skyblue')
        #Label(f_photo,text="Photo : ",font=('',15),background='skyblue').pack(side='left')
        #Button(f_photo,text='parcourir').pack(side='right') #   parcourir nest pas implementer
        #Entry(f_photo,textvariable=var_photo,state='readonly').pack(side='right')
        
        #f_photo.pack()
        
        f3 = Frame(frame,background='skyblue')
        Button(f3,text="Modifier",command=ret,pady=10,padx=10,width=10).pack(side='left')
        Button(f3,text='Annuler',padx=10,pady=10,width=15,command=lambda: self.show_frame('Home')).pack(side='right')
        f3.pack(side='bottom',padx=10,pady=10)
        
        return frame

    def ResetPasswd(self,container):
        def ret():
            if var_confim_passwd.get() != var_passwd.get():
                alert_wn("Les deux champs doivent etre identique")
                return 
            
            param = {'password':var_passwd.get(),'confirm_password':var_confim_passwd.get(),'login_id':var_login_id.get()}
            try:
                api = API(setting.get('url'),'',cookie=temp_setting.cookie)
                api.reset_passwd(param)
            except Exception as e:
                alert_wn(e)
            else:
                alert_wn('Mot de passe chnger avec succes')
                self.show_frame('Home')
        
        frame = Frame(container,name='frame_resetpasswd',background='skyblue')
        
        var_login_id = StringVar(frame,name='var_login_id')

        var_passwd = StringVar(frame,name='var_passwd')
        var_confim_passwd = StringVar(frame,name='var_confirm_passwd')
        Label(frame,text="Changement de mot de passe",font=('',15),background='skyblue').pack()
        f1 = Frame(frame,background='skyblue')
        Label(f1,text="Mot de passe :",background='skyblue').pack(side='left')
        Entry(f1,textvariable=var_passwd,show='*').pack(side='right')
        f1.pack()
        f2 = Frame(frame,background='skyblue')
        Label(f2,text="Confirmer le :",background='skyblue').pack(side='left')
        Entry(f2,textvariable=var_confim_passwd,show='*').pack(side='right')
        f2.pack()
        
        f3 = Frame(frame,background='skyblue')
        Button(f3,text='Envoyer',padx=10,pady=10,width=15,command=ret).pack(side='left')
        Button(f3,text='Annuler',padx=10,pady=10,width=15,command=lambda: self.show_frame('Home')).pack(side='right')
        f3.pack(side='bottom',padx=10,pady=10)
        
        
        return frame


class SessionPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller 
        self.tab_index = {}
        self.data = {}
        self.users = {}
        
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

        Label(frame,text="Sessions",font=('',15),background='skyblue').pack(padx=5,pady=5)

        f1 = Frame(frame,background='skyblue',name='body')
        lc = ttk.Treeview(f1,columns=('id','usernames','date','statut','ip'),name='tableau')
        lc.heading('id',text="Id")
        lc.heading('usernames',text='Usernames')
        lc.heading('date',text="Date")
        lc.heading('statut',text="Statut")
        lc.heading('ip',text="Addresse IP")

        lc['show'] = 'headings'

        sc = Scrollbar(f1,command=lc.yview)
        sc.pack(side="right",fill=Y)

        lc.configure(yscrollcommand=sc.set)

        lc.pack(fill="both", expand=True)

        f1.pack(fill="both", expand=True)

        f_both = Frame(frame,padx=10,pady=10,background='skyblue')
        Button(f_both,text='Bloquer',command=self.block).pack(side='left')
        Button(f_both,text='Supprimer',command=self.delete).pack(side='right')
        f_both.pack(side='bottom')
        
        return frame

    def actualise(self):
        try:
            api = API(setting.get('url'),'sessions',cookie=temp_setting.cookie)
            data = api.all()
        except Exception as e:
            alert_wn(e)
        else:
            lc = self.frames['Home'].nametowidget('body.tableau')
            for i, d in data.items():
                p = (
                    d.get('session_id'),
                    d.get('username'),
                    d.get('date'),
                    'actif' if d.get('statut') == 1 else 'bloquer',
                    d.get('ip_addr')
                    )
                if not lc.exists(int(i)):
                    lc.insert('','end',iid=d.get('session_id'),values=p)

    def block(self):
        lc = self.frames['Home'].nametowidget('body.tableau')
        i = lc.selection()
        if not i:
            return
        
        session = i[0]
        param = {'session_id':session}
        try:
            api = API(setting.get('url'),'sessions',cookie=temp_setting.cookie)
            api.change(param)
        except Exception as e:
            alert_wn(e)
        else:
            lc.set(session,'statut','bloquer')

    def delete(self):
        lc = self.frames['Home'].nametowidget('body.tableau')
        i = lc.selection()
        if not i:
            return
        
        session = i[0]
        try:
            api = API(setting.get('url'),'sessions',cookie=temp_setting.cookie)
            api.delete(session)
        except Exception as e:
            alert_wn(e)
        else:
            lc.delete(session)
 


class MonitorPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
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


    def Home(self,contenair):
        frame = Frame(contenair,name='frame_home',background='skyblue')
        Label(frame,text='Monitoring',font=('',24),background='skyblue').pack(padx=5,pady=5)

        tab = ttk.Treeview(frame,columns=('id','action','message','date'),height=30,name='tableau')
        tab.heading('id',text="Id")
        tab.column('id',width=30)
        tab.heading('action',text='Action')
        tab.column('action',width=50)
        tab.heading('message',text="Message",)
        tab.column('message',width=395)
        tab.heading('date',text="Date")
        #self.tab.column('date',width=35)
        tab['show'] = 'headings'
        frame.bind('<Control-A>' or '<Control-a>',self.actualise)

        sc = Scrollbar(frame,command=tab.yview)
        sc.pack(side="right",fill=Y)

        tab.configure(yscrollcommand=sc.set)
        
        tab.pack(expand=True,fill='both')
        
        return frame

    def actualise(self):
        try:
            api = API(setting.get('url'),'logs',cookie=temp_setting.cookie)
            data = api.all()
        except Exception as e:
            alert_wn(e)
        else:
            tableau = self.frames['Home'].nametowidget('tableau')
            for id_ , value in data.items():
                if not tableau.exists(id_):
                    p = (
                        id_,value.get('action'),value.get('message'),value.get('date')
                    )
                    tableau.insert('','end',iid=id_,values=p)
