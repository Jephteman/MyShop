from .utils import *
from tkinter import *
from tkinter import ttk

# jai pas encore rendu les derniers optimisation
class users_admin:
    def __init__(self):
        "intervient dans l'administration des comptes sur le backend"

        self.tab_index = {}
        self.data = {}

        self.window = Toplevel(class_='utilisateurs')
        self.window.resizable(False,False)

        Label(self.window,text="Utilisateurs",font=('',15)).pack(padx=5,pady=5)

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
            for i in data1.keys():
                d = data1.get(i)

                try:
                    d.update(data2.get(i))
                except :
                    continue

                self.data[i] = d
        except InterruptedError as e:
            alert_wn(e)
            self.window.destroy()
        else:
            for index, info in self.data.items() : 
                if not self.lc.exists(int(index)):
                    x =  self.lc.insert('','end',iid=index,values=(int(index),info.get('username'),info.get('noms'),info.get('role'),'actif' if info.get('statut') else 'bloquer'))

    def add(self):
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
                'photo':''
            }
            if self.var_photo.get():
                photo = open(self.var_photo,'rb').read()
                photo = base64.encodebytes(photo)
                param['photo'] = photo

            try:
                api = client.API('users')
                data = api.add(param)
            except Exception as e:
                alert_wn(e)
            else:
                window.destroy()
                data.update(param)
                self.data[str(data.get('login_id'))] = data
                i_ = str(data.get('login_id'))
                x =  self.lc.insert('','end',iid=i_,values=(
                    i_,data.get('username'),
                    data.get('noms'),data.get('role'),
                    'actif'))
                alert_wn("Le compte a été crée avec success")
        
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
        self.var_photo = StringVar(window)

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
        Button(f_photo,text='parcourir',command=self.set_file).pack(side='right') #   parcourir nest pas implementer
        Entry(f_photo,textvariable=self.var_photo,state='readonly').pack(side='right')
        

        f_photo.pack()

        Button(window,text="Creer le compte",command=ret,font=('',15),pady=15,width=25).pack()

    def set_file(self):
        t = [('Image File','*.png'),('Image File','*.jpg')]
        askfile_open(self.var_photo,t)

    def delete(self):
        def ret():
            try:
                api = client.API('users')
                api.delete(user_id)
            except Exception as e:
                alert_wn(e)
            else:
                window.destroy()
                self.lc.delete(user_id)
        
        i = self.lc.selection()
        if not i:
            return
        
        user_id = i[0]
        
        window = Toplevel(self.window,height=100,width=100)
        window.resizable(False,False)

        Label(window,text=f"Voullez-vous supprimer l'utilisateur {self.data[user_id].get('username')} ?",padx=10,font=('',13),).pack()

        f1 = Frame(window)
        Button(f1,text="  OUI  ",font=('',9),command=ret,pady=6,width=10).pack(side=LEFT)
        Button(f1,text='  NON  ',command=window.destroy,font=('',9),pady=6,width=10).pack(side=RIGHT)
        f1.pack()

    def change(self):
        
        def ret():
            param = {
                'login_id':login_id,
                'user_id':login_id,
                'noms':var_noms.get(),
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
                self.lc.delete(i[0])
                self.lc.insert(
                    '',i[0],iid=i[0],values=(
                        i[0],user_info.get('username'),
                        param.get('noms'),param.get('role'),
                        'actif' if user_info.get('statut') else 'bloquer')
                    )
                
                alert_wn("Le compte a ete modifier avec success")

        i = self.lc.selection()
        if not i :
            return
        
        
        login_id = i[0]
        user_info = self.data.get(login_id)
        
        window = Toplevel(self.window)
        window.geometry('600x400')
        window.resizable(False,False)

        var_role = StringVar(window,value=user_info.get('role'))
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
        
        login_id = i[0]

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

        Label(window,text="Sessions",font=('',15)).pack(padx=5,pady=5)

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
            api = client.API('sessions')
            data = api.all()
        except Exception as e:
            alert_wn(e)
        else:
            for i, d in data.items():
                p = [
                    d.get('session_id'),
                    d.get('username'),
                    d.get('date'),
                    'actif' if d.get('statut') == 1 else 'bloquer',
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
 

