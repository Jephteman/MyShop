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
        for F in (self.Home, self.Add, self.ResetPasswd):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Afficher la première frame
        self.show_frame("Home")
        
    def show_frame(self, cont, action=''):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        clean_variable(frame)
        if action or cont == 'ResetPasswd':
            tab = self.frames['Home'].nametowidget('body.tableau')
            try:
                login_id = tab.selection()[0]
            except Exception as e:
                alert_wn(e)
                return
                
            if action == 'see':
                entry_passwd = self.frames['Add'].nametowidget('frame_password.entry_password').config(state='readonly')
                entry_username = self.frames['Add'].nametowidget('frame_username.entry_username').config(state='readonly')
                data = self.data.get(login_id)
            
                frame.setvar('var_uname',data.get('username'))
                frame.setvar('var_passwd',data.get('password',''))
                frame.setvar('var_addr',data.get('addr'))
                frame.setvar('var_noms',data.get('noms'))
                frame.setvar('var_tel',data.get('telephone',''))
                frame.setvar('var_email',data.get('email',''))
                #frame.setvar('var_photo',data.get('photo'))
                frame.setvar('var_role',data.get('role'))
                
            frame.setvar('var_login_id',login_id)

        elif (cont == 'Add') and not action :
            entry_passwd = self.frames['Add'].nametowidget('frame_password.entry_password').config(state='normal')
            entry_username = self.frames['Add'].nametowidget('frame_username.entry_username').config(state='normal')
                
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
        Button(f_both,text='Change',command=lambda : self.show_frame('Add',action='see')).pack(side='left')
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
                'login_id':var_login_id.get(),
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
                if var_login_id.get():
                    api.change(param)
                else:
                    data = api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                self.data[str(data.get('login_id'))] = data
                lc = self.frames['Home'].nametowidget('body.tableau')
                i_ = str(data.get('login_id'))
                if param.get('login_id'):
                    i = lc.selection()
                    lc.delete(i[0])

                lc.insert('','end',iid=i_,values=(
                    i_,data.get('username'),
                    data.get('noms'),data.get('role'),
                    'actif'))
                alert_wn("Le compte a été crée avec success")
                self.show_frame('Home')

        frame = Frame(container,name='frame_add',background='skyblue')
        var_login_id = StringVar(frame,name='var_login_id')
        var_role = StringVar(frame,name='var_role')
        var_uname = StringVar(frame,name='var_uname')
        var_passwd = StringVar(frame,name='var_passwd')
        var_addr = StringVar(frame,name='var_addr')
        var_noms = StringVar(frame,name='var_noms')
        var_tel = StringVar(frame,name='var_tel')
        var_email = StringVar(frame,name='var_email')
        #var_photo = StringVar(frame,name='var_photo')

        Label(frame,text="Création d'un compte",font=('',29),pady=15,background='skyblue').pack()

        EntryWithLabel(frame,label_text='Nom :',variable_text='var_noms')
        EntryWithLabel(frame,label_text="Nom d'utilisateur :",variable_text='var_uname',entry_cnf={'name':'entry_username'},frame_name='frame_username')
        EntryWithLabel(frame,label_text="Mot de pass :",variable_text='var_passwd',entry_cnf={'show':'*','name':'entry_password'},frame_name='frame_password')
        ComboboxWithLabel(frame,textvariable=var_role,combox_cnf={'values':('admin','vendeur','moniteur')},label_text='Role : ')

        EntryWithLabel(frame,label_text='Addresse :',variable_text='var_addr')
        EntryWithLabel(frame,label_text='Telephone :',variable_text='var_tel')
        EntryWithLabel(frame,label_text='Email :',variable_text='var_email')
        
        f3 = Frame(frame,background='skyblue')
        Button(f3,text="Envoyer",command=ret,pady=10,width=20).pack(side='left')
        Button(f3,text='Annuler',padx=10,pady=10,width=15,command=lambda: self.show_frame('Home')).pack(side='right')
        f3.pack(padx=10,pady=10,side='bottom')

        
        return frame

    def delete(self):
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

        EntryWithLabel(frame,label_text="Mot de passe :",variable_text='var_passwd',entry_cnf={'show':'*'})
        EntryWithLabel(frame,label_text="Confirmer le :",variable_text='var_confirm_passwd',entry_cnf={'show':'*'})
        
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
        try:
            lc = self.frames['Home'].nametowidget('body.tableau')
            i = lc.selection()
        
            session = i[0]
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
