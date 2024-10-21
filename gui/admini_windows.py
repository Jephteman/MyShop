from config import * 
from utils import *
from tkinter import *
from tkinter import ttk
from dateutil.parser import parser as parser_date

class users_admin:
    def __init__(self):
        "intervient dans l'administration des comptes sur le backend"

        self.tab_index = {}
        self.data = {}

        self.window = Toplevel(class_='utilisateurs')
        self.window.resizable(False,False)

        f1 = Frame(self.window,padx=10,pady=10)
        self.lc = ttk.Treeview(f1,columns=('id','usernames','noms','role','statut'))
        self.lc.heading('id',text="Id")
        self.lc.heading('usernames',text='Usernames')
        self.lc.heading('noms',text="Noms")
        self.lc.heading('role',text="Role")
        self.lc.heading('statut',text="Statut")
        self.lc['show']='headings'

        sc = Scrollbar(self.window,command=self.lc.yview)
        sc.pack(side="right",fill=Y)

        self.lc.configure(yscrollcommand=sc.set)

        self.lc.pack()

        f1.pack()

        f_both = Frame(self.window,padx=10,pady=10)
        Button(f_both,text='Ajouter',command=self.add).pack(side='left')
        Button(f_both,text='Change',command=self.change).pack(side='left')
        Button(f_both,text="Changer le mdp",command=self.reset_passwd).pack(side='left')
        Button(f_both,text='Delete',command=self.delete).pack(side='right')


        f_both.pack(side='bottom')

        self.actualise()
    
    def actualise(self):
        self.data = {}
        try:
            data1 = client.API('users').all()
            data2 = client.API('agents').all()

            for i in range(0,len(data1)):
                 self.data.update({
                    data1[i].get('login_id'):dict(
                    list(data1[i].items()) + list(data2[i].items())
                    )
                })

        except Exception as e:
            alert_wn(e)
            self.window.destroy()
        else:
            for index, info in self.data.items() : 
                if not self.lc.exists(int(index)):
                    x =  self.lc.insert('','end',iid=int(index),values=(int(index),info.get('username'),info.get('noms'),info.get('role'),'actif' if info.get('statut') else 'bloquer'))
                    self.tab_index.update({x:index})

    def add(self):
        def ret():
            param = {
                'noms':var_noms.get(),
                'username':var_uname.get(),
                'password':var_passwd.get(),
                'addr':var_addr.get(),
                'role':var_role.get(),
                'telephone':var_tel.get(),
                'email':var_email.get(),
                'photo':'' # nous devons avoir une foction qui encode en base64 limage 
            }

            try:
                api = client.API('users')
                api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                window.destroy()
                self.actualise()
                alert_wn("Le compte a ete creer avec success")
        
        window = Toplevel(self.window)
        window.geometry('600x400')
        window.resizable(False,False)

        var_role = StringVar(window)
        var_uname = StringVar(window)
        var_passwd = StringVar(window)
        var_addr = StringVar(window)
        var_noms = StringVar(window)
        var_tel = StringVar(window)
        var_email = StringVar(window)
        var_photo = StringVar(window)

        Label(window,text="Création d'un compte",font=('',29),pady=15).pack()

        f_noms = Frame(window)
        Label(f_noms,text="Noms : ",font=('',15)).pack(side='left')
        Entry(f_noms,textvariable=var_noms).pack(side='right')
        f_noms.pack()

        f_uname = Frame(window)
        Label(f_uname,text="Nom d'utilisateur : ",font=('',15)).pack(side='left')
        Entry(f_uname,textvariable=var_uname).pack(side='right')
        f_uname.pack()

        f_pass = Frame(window)
        Label(f_pass,text="Mot de passe : ",font=('',15)).pack(side='left')
        Entry(f_pass,textvariable=var_passwd).pack(side='right')
        f_pass.pack()

        f_role = Frame(window)
        Label(f_role,text="Role : ",font=('',15)).pack(side='left')
        ttk.Combobox(f_role,textvariable=var_role,values=('admin','vendeur','moniteur')).pack(side='right')
        f_role.pack()

        f_addr = Frame(window)
        Label(f_addr,text="Addrese : ",font=('',15)).pack(side='left')
        Entry(f_addr,textvariable=var_addr).pack(side='right')
        f_addr.pack()

        f_num = Frame(window)
        Label(f_num,text="Numero : ",font=('',15)).pack(side='left')
        Entry(f_num,textvariable=var_tel).pack(side='right')
        f_num.pack()

        f_mail = Frame(window)
        Label(f_mail,text="Email : ",font=('',15)).pack(side='left')
        Entry(f_mail,textvariable=var_email).pack(side='right')
        f_mail.pack()

        f_photo = Frame(window)
        Label(f_photo,text="Photo : ",font=('',15)).pack(side='left')
        Button(f_photo,text='parcourir').pack(side='right') #   parcourir nest pas implementer
        Entry(f_photo,textvariable=var_photo,state='readonly').pack(side='right')
        

        f_photo.pack()

        Button(window,text="Creer le compte",command=ret,font=('',15),pady=15,width=25).pack()

    def delete(self):
        def ret():
            try:
                api = client.API('users')
                api.delete(user_id)
            except Exception as e:
                alert_wn(e)
                window.destroy()
            else:
                window.destroy()
                self.lc.delete(i[0])
        
        i = self.lc.selection()
        if not i:
            return
        
        user_id = self.tab_index.get(i[0])
        user_info = self.data.get(user_id)
        
        window = Toplevel(self.window,height=100,width=100)
        window.resizable(False,False)

        Label(window,text=f"Voullez-vous supprimer l'utilisateur {user_info.get('username')} ?",padx=10,font=('',13),).pack()

        f1 = Frame(window)
        Button(f1,text="  OUI  ",font=('',9),command=ret,pady=6,width=10).pack(side=LEFT)
        Button(f1,text='  NON  ',command=window.destroy,font=('',9),pady=6,width=10).pack(side=RIGHT)
        f1.pack()

    def change(self):
        
        def ret():
            param = {
                'login_id':login_id,
                'noms':var_noms.get(),
                'username':var_uname.get(),
                'addr':var_addr.get(),
                'role':var_role.get(),
                'telephone':var_tel.get(),
                'email':var_email.get(),
                'photo':'' # nous devons avoir une foction qui encode en base64 limage 
            }

            try:
                api = client.API('users')
                api.change(param)
            except Exception as e:
                alert_wn(e)
            else:
                window.destroy()
                self.lc.insert(
                    '',i[0],values=(
                        int(i[0]),param.get('username'),
                        param.get('noms'),param.get('role'),
                        'actif' if param.get('statut') else 'bloquer')
                    )
                
                alert_wn("Le compte a ete creer avec success")

        i = self.lc.selection()
        if not i :
            return
        
        
        login_id = self.tab_index[i[0]]
        user_info = self.data.get(login_id)
        
        window = Toplevel(self.window)
        window.geometry('600x400')
        window.resizable(False,False)

        var_role = StringVar(window,value=user_info.get('role'))
        var_uname = StringVar(window,value=user_info.get('username'))
        var_addr = StringVar(window,value=user_info.get('addr'))
        var_noms = StringVar(window,value=user_info.get('noms'))
        var_tel = StringVar(window,value=user_info.get('telephone'))
        var_email = StringVar(window,value=user_info.get('email'))
        var_photo = StringVar(window)

        Label(window,text="Modification d'un compte",font=('',29),pady=15).pack()

        f_noms = Frame(window)
        Label(f_noms,text="Noms : ",font=('',15)).pack(side='left')
        Entry(f_noms,textvariable=var_noms).pack(side='right')
        f_noms.pack()

        f_uname = Frame(window)
        Label(f_uname,text="Nom d'utilisateur : ",font=('',15)).pack(side='left')
        Entry(f_uname,textvariable=var_uname).pack(side='right')
        f_uname.pack()

        f_role = Frame(window)
        Label(f_role,text="Role : ",font=('',15)).pack(side='left')
        ttk.Combobox(f_role,textvariable=var_role,values=('admin','vendeur','moniteur')).pack(side='right')
        f_role.pack()

        f_addr = Frame(window)
        Label(f_addr,text="Addrese : ",font=('',15)).pack(side='left')
        Entry(f_addr,textvariable=var_addr).pack(side='right')
        f_addr.pack()

        f_num = Frame(window)
        Label(f_num,text="Numero : ",font=('',15)).pack(side='left')
        Entry(f_num,textvariable=var_tel).pack(side='right')
        f_num.pack()

        f_mail = Frame(window)
        Label(f_mail,text="Email : ",font=('',15)).pack(side='left')
        Entry(f_mail,textvariable=var_email).pack(side='right')
        f_mail.pack()

        f_photo = Frame(window)
        Label(f_photo,text="Photo : ",font=('',15)).pack(side='left')
        Button(f_photo,text='parcourir').pack(side='right') #   parcourir nest pas implementer
        Entry(f_photo,textvariable=var_photo,state='readonly').pack(side='right')
        

        f_photo.pack()

        Button(window,text="Modifier",command=ret,font=('',15),pady=15,width=25).pack()

    def reset_passwd(self):
        def ret():
            if var_confim_passwd.get() != var_passwd.get():
                alert_wn("Les deux champs doivent etre identique")
                return 
            
            param = {'password':var_passwd.get(),'confirm_password':var_confim_passwd.get(),'login_id':login_id}
            try:
                api = client.API('')
                api.reset_passwd(param)
            except Exception as e:
                alert_wn(e)
            else:
                alert_wn('Mot de passe chnger avec succes')
                window.destroy()
            
        i = self.lc.selection()
        if not i:
            return 
        
        login_id = self.tab_index[i[0]]

        window = Toplevel(self.window)
        var_passwd = StringVar(window)
        var_confim_passwd = StringVar(window)
        Label(window,text="Changement de mot de passe",font=('',15)).pack()
        f1 = Frame(window)
        Label(f1,text="Mot de passe :").pack(side='left')
        Entry(f1,textvariable=var_passwd,show='*').pack(side='right')
        f1.pack()
        f2 = Frame(window)
        Label(f2,text="Confirmer le :").pack(side='left')
        Entry(f2,textvariable=var_confim_passwd,show='*').pack(side='right')
        f2.pack()
        Button(window,text='Envoyer',padx=10,pady=10,width=15,command=ret).pack()

class session_admin:
    def __init__(self):
        self.users = {}

        window = Toplevel(class_='sessions')
        window.resizable(False,False)

        f1 = Frame(window,padx=10,pady=10)
        self.lc = ttk.Treeview(f1,columns=('id','usernames','date','statut','ip'))
        self.lc.heading('id',text="Id")
        self.lc.heading('usernames',text='Usernames')
        self.lc.heading('date',text="Date")
        self.lc.heading('statut',text="Statut")
        self.lc.heading('ip',text="Addresse IP")

        self.lc['show'] = 'headings'

        sc = Scrollbar(window,command=self.lc.yview)
        sc.pack(side="right",fill=Y)

        self.lc.configure(yscrollcommand=sc.set)

        self.lc.pack()

        f1.pack()

        f_both = Frame(window,padx=10,pady=10)
        Button(f_both,text='Bloquer',command=self.block).pack(side='left')
        Button(f_both,text='Supprimer',command=self.delete).pack(side='right')

        try:
            api = client.API('users')
            for i in api.all():
                self.users.update({i.get('login_id'):i.get('username')})

            api = client.API('sessions')
            data = api.all()
        except Exception as e:
            alert_wn(e)
        else:
            for d in data:
                p = [
                    d.get('session_id'),
                    self.users.get(d.get('login_id')),
                    d.get('date'),
                    'actif' if d.get('statut') else 'bloquer',
                    d.get('ip_addr')
                    ]
                self.lc.insert('','end',iid=d.get('session_id'),values=p)

        f_both.pack(side='bottom')

    def block(self):
        i = self.lc.selection()
        if not i:
            return
        
        session = i[0]
        param = {'session_id':session}
        try:
            api = client.API('sessions')
            api.change(param)
        except Exception as e:
            alert_wn(e)
        else:
            self.lc.set(session,'statut','bloquer')

    def delete(self):
        i = self.lc.selection()
        if not i:
            return
        
        session = i[0]
        try:
            api = client.API('sessions')
            api.delete(session)
        except Exception as e:
            alert_wn(e)
        else:
            self.lc.delete(session)

class inventaire:
    def __init__(self):
        self.exist_item = []
        self.users = {}

        self.window = Toplevel(class_="inventaire",width=500)
        self.window.resizable(False,False)
        # en-tete  
        self.origine = StringVar()
        self.fin = StringVar()
        self.somme = IntVar()

        f1 = Frame(self.window,padx=10,pady=10)
        Label(f1,text='A partir du ').pack(side='left')
        Entry(f1,textvariable=self.origine,).pack(side='left')
        Label(f1,text="Au ").pack(side='left')
        Entry(f1,textvariable=self.fin).pack(side='left')
        Button(f1,text="Chercher",command=self.find).pack(side='left')
        f1.pack()

        f2 = Frame(self.window,height=200)
        self.lc = ttk.Treeview(f2,columns=('id','client_id','march','vendeur','prix'))
        self.lc.heading('id',text="Id")
        self.lc.column('id',width=35)
        self.lc.heading('client_id',text="Client id")
        self.lc.heading('march',text='Marchandises')
        self.lc.heading('vendeur',text="Vendeur")
        self.lc.heading('prix',text="Prix")
        
        self.lc['show'] = 'headings'

        sc=Scrollbar(f2,command=self.lc.yview,)
        sc.pack(side="right",fill='both')

        self.lc.configure(yscrollcommand=sc.set)

        self.lc.pack(pady=20,padx=10)

        f2.pack()

        f3 = Frame(self.window)
        Label(f3,text='Total : ').pack(side='left')
        Label(f3,textvariable=self.somme).pack(side='left')
        f3.pack()

        self.find()
 
    def find(self):
        def check_form(date):
            date = date.strip()
            if date == '':
                return
            
            try:
                return parser_date().parse(date).strftime("%Y-%m-%d")
            except Exception:
                raise Exception("Mauvais formant, veillez inserer 'annee/mois/jour'")

        try:
            from_ = check_form(self.origine.get())
            to = check_form(self.fin.get())

            param = None
            if from_ and to:
                param = {'from':from_,'to':to}


            api = client.API('users')
            for i in api.all():
                self.users.update({i.get('login_id'):i.get('username')})

            api = client.API('ventes')
            data = api.all(param=param)
        except Exception as e:
            alert_wn(e)
        else:
            self.somme.set(0)
            
            for i in self.exist_item:
                self.lc.delete(i)

            self.exist_item.clear()

            for info in data:
                p = [
                    info.get('vente_id'), self.users.get(info.get('client_id')),
                    info.get('marchandises'),info.get('login_id'),info.get('prix')]
                item = self.lc.insert('','end',iid=info.get('vente_id'),values=p)
                self.exist_item.append(item)
                self.somme.set(self.somme.get() + info.get('prix'))
        

    