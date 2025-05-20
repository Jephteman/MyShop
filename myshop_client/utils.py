from .client import API

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile
from configparser import ConfigParser
from json import JSONDecoder , JSONEncoder

import os
import csv
import base64
import platform
import pathlib
import tempfile
import datetime
import matplotlib.pyplot as plt 

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image as rep_image
import pkg_resources

try:
    import pywin32_system32 as win32
except:
    if os.name == 'nt':
        print("Vous ne pourrez pas effectuer d'impression puis que vous n'avez installé 'win32print'")


class Config:
    def __init__(self,temp_file=False):
        self.temp_file = temp_file
        self.config = ConfigParser(allow_no_value=True)
        
        if not temp_file:
            if platform.system() == "Windows":
                config_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "myshop")
            else:
                config_dir = os.path.expanduser("~/.config/myshop")

            config_file = os.path.join(config_dir, "config.txt")
            self.conf_file = pathlib.Path(config_file)
            self.config.read(config_file)
            
        self.cookie = {}
    
    def is_installed(self):
        return True if self.get('url') != '' else False

    def save(self):
        if self.temp_file:
            raise Exception("Fichier temporaire ne peut etre stocker")
        with open(self.conf_file,'w') as f:
            self.config.write(f)
            alert_wn("Pour appliquer les parametres, veillez redemarer le programme")

    def get(self,param:str):
        return self.config.get('CLIENT',param) if self.config.has_option('CLIENT',param) else ''

    def set(self,param,value):
        if not self.config.has_section('CLIENT'):
            self.config['CLIENT'] = {}
        self.config["CLIENT"][param] = value

    def all(self): # retourne tous les parametres du clients
        return self.config['CLIENT']

    def update_cookie(self):
        cookie = self.get('cookie')
        self.cookie = JSONDecoder().decode(cookie)

def askfile_save(var,file_type):
    x = asksaveasfile(filetypes=file_type)
    if x:
        var.set(x.name)
        x.close()

def askfile_open(var,file_type):
    # [('Image File','*.png'),('Image File','*.jpg')]
    x = askopenfilename(filetypes=file_type)
    if x:
        var.set(x)

def alert_wn(message):
    print(message)
    f = Toplevel()
    f.title("Alert")
    f.geometry("550x100")
    f.resizable(False,False)
    Label(f,text=message,height=3,relief='solid',wraplength=540).pack()
    Button(f,text='OK',command=f.destroy).pack(side='bottom')

def login_wn():
    temp_setting.set('is_login','no')
    def check():
        data = {'username':u.get(),'password':p.get()}
        resp = API(setting.get('url'),'')
        try:
            config_serv = resp.connect(data)
            for label, value in config_serv.items():
                if type(value) is dict:
                    value = JSONEncoder().encode(value)
                if value == None:
                    value = ''
                temp_setting.set(label,value)
            root.destroy()
        except Exception as e:
            alert_wn(e)
        else:
            temp_setting.set('is_login','yes')
            temp_setting.update_cookie()
    
    cookie = setting.get('cookie')
    if (setting.get('auto_login') == 'OUI') and cookie:
        setting.update_cookie()
        is_valid = API(setting.get('url'),'',cookie=setting.cookie).check_cookie()
        if is_valid:
            for label, value in is_valid.items():
                if type(value) is dict:
                    value = JSONEncoder().encode(value)
                elif value == None:
                    value = ''
                else :
                    value = str(value)
                temp_setting.set(label,value)
            temp_setting.set('is_login','yes')
            temp_setting.cookie = setting.cookie
            return 
        
    root = Tk()
    root.config(background='skyblue')
    #logo = pkg_resources.resource_filename('myshop','logo.ico')
    #root.iconbitmap(logo)
    u = StringVar()
    p = StringVar()
    root.title("Connection")
    root.resizable(False,False)
    Label(root,text="Connection au serveur",font=('',15),wraplength=540,padx=10,pady=10).pack()
    
    f1 = Frame(root,padx=8,pady=8,background='skyblue')
    Label(f1,text="Nom d'utilisateur : ").pack(side='left')
    Entry(f1,textvariable=u).pack(side='right')
    f1.pack()

    f2 = Frame(root,padx=8,pady=8,background='skyblue')
    Label(f2,text="Mot de passe   : ").pack(side='left')
    Entry(f2,textvariable=p,show='*').pack(side='right')
    f2.pack()

    Button(root,text='Connecter',command=check,padx=8,pady=8,width=15).pack()

    root.mainloop()

def about():
    f = Toplevel(background='skyblue')
    f.geometry('500x550')
    f.resizable(width=False,height=False)
    Label(f,text='\nCe programme a été developpé sous license GNU/Linux \n').pack()
    Label(f,text='Pour asurrer la gestion d\'une boutique ou quelque chose du genre ').pack()
    """Quelques ajout"""
    Label(f,text="Contact : Jephte Mangenda ( tech5industrie@gmail.com ) ").pack(side='bottom')
    Label(f,text="Disponible sur : https://github.com/Jephteman/MyShop").pack(side='bottom')
    Label(f,text=f"Version : {version}").pack(side='bottom')

def save_cookie(): # save cookie in permenante setting
    setting.set('cookie',temp_setting.get('cookie'))

"""Setup process"""
class setup:
    def __init__(self):
        self.list_wind = {0:self.setup0,1:self.setup1,2:self.setup2}
        self.config = ConfigParser()
        self.etape = 0
        self.root = Tk(className=f"Installation MyShop {version}")
        self.root.geometry('720x520')
        self.root.resizable(height=False,width=False)
        self.root.config(background='skyblue')

        # le frame rotatif , qui peu changer des text ou delement 
        self.p_frame = Frame(self.root,width=700,height=500,padx=10,pady=10,background='skyblue')


        f_both = Frame(self.root,background='skyblue')

        self.b_prev = Button(f_both,text="Precedent",command=self.prev)
        self.b_prev.pack(side="left")
        self.b_next = Button(f_both,text="Suivant",command=self.next)
        self.b_next.pack(side='left')
        self.b_fin = Button(f_both,text="Terminer",command=self.root.destroy,state='disabled')
        self.b_fin.pack(side='left')
        f_both.pack(side='bottom')

        self.setup0()
        self.p_frame.pack()

        self.root.mainloop()

    def next(self):
        self.frame.destroy()
        self.etape += 1
        self.list_wind[self.etape]()

    def prev(self):
        self.frame.destroy()
        self.etape -= 1
        self.list_wind[self.etape]()

    def setup0(self):
        """Message de bienvenu et un bref message """
        self.b_prev.configure(state='disabled')
        self.frame = Frame(self.p_frame,width=700,height=500,padx=10,pady=10,background='skyblue')
        Label(self.frame,text="\n BIENVENU \n",font=('',21)).pack()
        text = """
            Ce programme a été concu pour faciliter la gestion d'une boutique  \n
            Ce programme à été ecrit par Jephte Mangenda ( tech5industrie@gmail.com )
            Vous pouvez le retrouver sur \n Github ( https://github.com/Jephteman/MyShop )
            Nous allons commencer la configuration du programme
            """
        Label(self.frame,text=text,font=('',11)).pack()
        self.frame.pack()

    def setup1(self):
        """ Choix du type de stockage"""

        self.b_prev.configure(state='active')

        self.frame = Frame(self.p_frame,padx=10,pady=10,background='skyblue')
        Label(self.frame,font= ('',23) ,text="CONFIGURATION \n").pack(side='top')
        Label(self.frame,text="Veillez remplir ce formulaire ",font=('',12)).pack()

        f1 = Frame(self.frame,background='skyblue')
        StringVar(self.root,name='url')
        Label(f1,text=f"Url du serveur : ",height=3).pack(side='left')
        Entry(f1,textvariable='url').pack(side="right")
        f1.pack()

        f1 = Frame(self.frame,background='skyblue')
        StringVar(self.root,name='proxy')
        Label(f1,text=f"Proxy : ",height=3).pack(side='left')
        Entry(f1,textvariable='proxy').pack(side="right")
        f1.pack()

        f1 = Frame(self.frame,background='skyblue')
        StringVar(self.root,name='theme')
        Label(f1,text=f"Theme : ",height=3).pack(side='left')
        ttk.Combobox(f1,textvariable='theme',values=['Jour','Nuit'],validate='focusin',).pack(side='right')
        f1.pack()

        f1 = Frame(self.frame,background='skyblue')
        StringVar(self.root,name='login_auto')
        Label(f1,text=f"Connection automatique : ",height=3).pack(side='left')
        Radiobutton(f1,text='OUI',variable='auto_login',value='OUI').pack(side='right')
        Radiobutton(f1,text='NON',variable='auto_login',value='NON',state='active').pack(side='right')
        f1.pack()
                
        self.frame.pack()
        
    def install(self):
        if not self.config.has_section('CLIENT'):
            self.config['CLIENT'] = {}
        
        self.config['CLIENT']['url'] = self.root.getvar('url')
        self.config['CLIENT']['proxy'] = self.root.getvar('proxy')
        self.config['CLIENT']['auto_login'] = self.root.getvar('auto_login')
        self.config['CLIENT']['theme'] = self.root.getvar('theme')
        # Détecter le système d'exploitation
        if platform.system() == "Windows":
            config_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "myshop")
        else:
            config_dir = os.path.expanduser("~/.config/myshop")

        config_file = os.path.join(config_dir, "config.txt")

        # Créer le dossier de configuration s'il n'existe pas
        os.makedirs(config_dir, exist_ok=True)

        try:
            with open(config_file,'a') as f:
                self.config.write(f)
        except Exception as e:
            alert_wn(e)
        else:
            return True

    def setup2(self):
        """ Choix du type de stockage"""

        self.b_prev.configure(state='active')

        if self.install():
            text = "Installation avec success"
            self.b_next.configure(state='disabled')
            self.b_fin.configure(state='active')
        else:
            text = "Echec de l'insatllation "

        self.frame = Frame(self.p_frame,background='skyblue')
        Label(self.frame,font= ('',23) ,text=" Resultat \n").pack(side='top')
        Label(self.frame,text=text,font=('',20)).pack()


        self.frame.pack()

class NotesPage():#tk.Frame):
    # def __init__(self, parent, controller):
    #     tk.Frame.__init__(self, parent)
    #     self.controller = controller
    def __init__(self):
    
        self.win = Toplevel(pady=5,padx=5,background='skyblue')
        self.notes = {}
        
        # Conteneur principal
        container = tk.Frame(self.win)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        
        # Création des différentes frames
        for F in (self.NoteHome, self.NoteAdd, self.NoteSee):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        try:
            api = API(setting.get('url'),'notes',cookie=temp_setting.cookie)
            self.notes.update(api.all())
        except Exception as e:
            alert_wn(e)
        
        self.show_frame('NoteAdd')
        
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        frame.tkraise()
        
        
    def NoteHome(self,contenair):
        frame = Frame(contenair)
        Label(frame,text='Notes',padx=5,pady=5,font=('',13)).pack()
        self.frame = Frame(self.win)
        f1 = Frame(self.frame,padx=3,pady=3,background='skyblue')
        self.tab = ttk.Treeview(f1,columns=('id','sujet','user','date'))#,height=30)
        self.tab.heading('id',text="Id")
        self.tab.heading('sujet',text="Sujet")
        self.tab.heading('user',text="Utilisateur")
        self.tab.heading('date',text="Date")

        self.tab['show'] = 'headings'

        sc = Scrollbar(f1,command=self.tab.yview)
        sc.pack(side="right",fill=Y)

        self.tab.configure(yscrollcommand=sc.set)
        
        self.tab.pack()

        f1.pack()

        f2 = Frame(self.frame,background='skyblue')

        Button(f2,text='Ajouter',padx=4,pady=4,command=self.add,width=10).pack(side='left')
        Button(f2,text='Voir',padx=4,pady=4,command=self.see,width=10).pack(side='left')
        Button(f2,text='Supprimer',padx=4,pady=4,command=self.delete,width=10).pack(side='right')

        f2.pack(side='bottom')

        for i , data in self.notes.items():
            n_id = str(data.get('note_id'))
            p = (n_id,data.get('sujet'),data.get('username'),data.get('date'))
            self.tab.insert('','end',iid=n_id,values=p)
            
        self.frame.pack()
        
    def add(self):
        self.frame.destroy()
        self.frame = Frame(self.win)
        def ret():
            param = {
                'sujet':var_sujet.get(),
                'description' : var_contenu.get('1.0','end-1c')
            }
            try:
                api = API(setting.get('url'),'notes',cookie=temp_setting.cookie)
                d = api.add(param)
            except Exception  as e:
                alert_wn(e)
            else:
                self.frame.destroy()
                self.frame1()
                d['username'] = setting.get('uname')
                n_id = str(d.get('note_id'))
                self.notes.update({n_id:d}),
                p = (n_id,d.get('sujet'),d.get('username'),d.get('date'))
                self.tab.insert('','end',iid=n_id,values=p)
                
                
        def annuler():
            self.frame.destroy()
            self.frame1()

        var_sujet = StringVar()

        f1 = Frame(self.frame,padx=5,pady=5,background='skyblue')
        Label(f1,text='Sujet : ').pack(side='left')
        Entry(f1,textvariable=var_sujet).pack(side='right')
        f1.pack()


        f3 = Frame(self.frame,background='skyblue')
        Label(f3,text='Contenu : ').pack(side='left')
        var_contenu = Text(f3,width=30,height=15)
        var_contenu.pack(side='right')
        f3.pack()
        f4 = Frame(self.frame)
        Button(f4,text='Envoyer',width=10,padx=5,pady=5,command=ret).pack(side='left')
        Button(f4,text='Annuler',width=10,padx=5,pady=5,command=annuler).pack(side='right')
        f4.pack(side='bottom')
        
        self.frame.pack()

    def see(self):
        def ret():
            self.frame.destroy()
            self.frame1()
        try:
            id_ = self.tab.selection()[0]
            data = self.notes.get(id_)
        except Exception as e:
            alert_wn(e)
        else:
            self.frame.destroy()
            self.frame = Frame(self.win)
            var_sujet = StringVar(value=data.get('sujet'))
            contenu = data.get('description')
            var_auth = StringVar(value=data.get('username'))

            f1 = Frame(self.frame,padx=3,pady=3,background='skyblue')
            Label(f1,text='Sujet : ').pack(side='left')
            Entry(f1,textvariable=var_sujet,state='readonly').pack(side='right')
            f1.pack()

            f2 = Frame(self.frame,padx=3,pady=3,background='skyblue')
            Label(f2,text='Auteur : ').pack(side='left')
            Entry(f2,textvariable=var_auth,state='readonly').pack(side='right')
            f2.pack()

            f3 = Frame(self.frame,padx=4,pady=4,background='skyblue')
            Label(f3,text='Contenu : ').pack(side='left')
            t = Text(f3,width=35,height=20)
            t.insert('end-1c',contenu)
            t.config(state='disabled')
            t.pack()
            f3.pack()
            Button(self.frame,text='Retour',width=10,padx=5,pady=5,command=ret).pack(side='bottom')
            self.frame.pack()

    def delete(self):
        try:
            id_ = self.tab.selection()[0]
            api = API(setting.get('url'),'notes',cookie=temp_setting.cookie)
            api.delete(id_)
        except Exception as e:
            alert_wn(e)
        else:
            try:
                self.tab.delete(id_)
                self.notes.pop(id_)
            except :
                pass

class monitoring:
    def __init__(self):
        win = Toplevel(name='monitoring',pady=5,padx=5,height=300,width=250,background='skyblue')
        Label(win,text='Monitoring',font=('',24)).pack(padx=5,pady=5)

        self.tab = ttk.Treeview(win,columns=('id','action','message','date'),height=30)
        self.tab.heading('id',text="Id")
        self.tab.column('id',width=30)
        self.tab.heading('action',text='Action')
        self.tab.column('action',width=50)
        self.tab.heading('message',text="Message",)
        self.tab.column('message',width=395)
        self.tab.heading('date',text="Date")
        #self.tab.column('date',width=35)
        self.tab['show'] = 'headings'
        win.bind('<Control-A>' or '<Control-a>',self.actualise)

        sc = Scrollbar(win,command=self.tab.yview)
        sc.pack(side="right",fill=Y)

        self.tab.configure(yscrollcommand=sc.set)
        
        self.tab.pack(expand=1,fill='x')
        self.actualise('')

    def actualise(self,event):
        try:
            api = API(setting.get('url'),'logs',cookie=temp_setting.cookie)
            data = api.all()
        except Exception as e:
            alert_wn(e)
        else:
            for id_ , value in data.items():
                if not self.tab.exists(id_):
                    p = (
                        id_,value.get('action'),value.get('message'),value.get('date')
                    )
                    self.tab.insert('','end',iid=id_,values=p)

class Graphique:
    def __init__(self):
        def set_file():
            file_t = [('File text','*.pdf')]
            askfile_save(self.path,file_t)

        self.window = Toplevel(width=500,padx=5,pady=5,background='skyblue')
        self.window.title('Graphique')
        self.window.resizable(False,False)
        
        # en-tete  
        self.origine = StringVar()
        self.fin = StringVar()
        self.path = StringVar()

        Label(self.window,text="Graphique",font=('',15)).pack()

        f1 = Frame(self.window,background='skyblue')
        Label(f1,text='A partir du ').pack(side='left')
        Entry(f1,textvariable=self.origine,).pack(side='left')
        Label(f1,text="Au ").pack(side='left')
        Entry(f1,textvariable=self.fin).pack(side='right')
        
        f1.pack()

        f2 = Frame(self.window,background='skyblue')
        Label(f2,text='Emplacement : ').pack(side='left')
        Entry(f2,textvariable=self.path,state='readonly').pack(side='left')
        Button(f2,text='parcourir',command=set_file).pack(side='right')

        f2.pack()

        Button(self.window,text="Generer",command=self.find).pack(side='bottom')

    def find(self):
        try:
            from_ = self.origine.get()
            to = self.fin.get()

            param = None
            if from_ and to:
                param = {'from':from_,'to':to,"isform":True}

            api = API(setting.get('url'),'ventes',cookie=temp_setting.cookie)
            data_raw = api.all(param=param)
        except IndentationError as e:
            alert_wn(e)
        else:
            self.window.destroy()
            dates = {}
            quantite = []
            for i , d in data_raw.items() :
                date = datetime.datetime.strptime(d.get('date').split(' ')[0],"%Y-%m-%d")
                if not date in dates.keys():
                    dates.update({date:0})

                dates[date] += 1
            
            file_save = self.path.get()

            plt.plot(dates.keys(),dates.values())
            plt.xlabel("Dates")
            plt.ylabel("Nombres")
            plt.title("Graphique des ventes")
            plt.gcf().autofmt_xdate()

            try:
                plt.savefig(file_save,format='pdf',bbox_inches='tight',)
            except IndentationError :
                alert_wn("Une ereur s'est produite")
                #plt.close()
            else:
                self.window.destroy()
                alert_wn("Le graphique est generer avec success")
            plt.close()

class Exporte:
    def __init__(self):
        win = Toplevel(background='skyblue')
        win.resizable(False,False)

        self.res = StringVar()
        self.path = StringVar()

        self.origine = StringVar()
        self.fin = StringVar()

        #win.title('Exportation des donnees')
        Label(win,text='Exportation des donnees',font=('',17),padx=5,pady=5).pack()

        f1 = Frame(win,background='skyblue')
        Label(f1,text='Ressource : ').pack(side='left')
        ttk.Combobox(f1,textvariable=self.res,values=('ventes','logs','arrivages','produits','notes','sessions')).pack(side='right')
        f1.pack()

        f2 = Frame(win,background='skyblue')
        Label(f2,text='A partir du ').pack(side='left')
        Entry(f2,textvariable=self.origine,).pack(side='left')
        Label(f2,text="Au ").pack(side='left')
        Entry(f2,textvariable=self.fin).pack(side='right')
        f2.pack()

        f3 = Frame(win,background='skyblue')
        Label(f3,text='Emplacement : ').pack(side='left')
        Entry(f3,textvariable=self.path,state='readonly').pack(side='left')
        Button(f3,text='Parcourir',command=self.set_file).pack(side='right')
        f3.pack()

        Button(win,text='Generer',padx=5,pady=5,command=self.generer).pack()

    def set_file(self):
        file_t = [('File text','*.csv')]
        askfile_save(self.path,file_t)

    def generer(self):   
        try:
            param = {
                'from':self.origine.get(),
                'to':self.fin.get(),
                'isreport':True
                }
            res = self.res.get()
            api = API(setting.get('url'),res,cookie=temp_setting.cookie)
            data = api.all(param)
        except Exception as e:
            alert_wn(e)
        else:
            serilise_data = []
            for  i, d in data.items():
                serilise_data.append(d)

            csv_file = self.path.get()
            if not serilise_data:
                alert_wn("Aucune donnee n'est disponible")
                return
            
            with open(csv_file,'w',newline='') as file:
                writer = csv.DictWriter(file,fieldnames=serilise_data[0].keys())
                writer.writeheader()
                writer.writerows(serilise_data)
            alert_wn('Donnees exportees avec success')
            
class Parametre:
    def __init__(self) -> None:
        self.window = Toplevel(background='skyblue')
        self.window.geometry('720x520')
        self.window.resizable(False,False)

        self.list_var = {
            'url':'str','proxy':'str',
            'theme':'choice',
            'auto_login':'radio_bouton' ,
            }

        Label(self.window,text='Parametre',font=('',24)).pack(padx=5,pady=5)

        f_dev = Frame(self.window,background='skyblue')

        for i, type_ in self.list_var.items():
            v = StringVar(self.window,name=i,value=setting.get(i))
            f_ = Frame(f_dev,background='skyblue')
            Label(f_,text=f'{i.capitalize()} : ').pack(side='left')
            if type_ == 'str':
                Entry(f_,textvariable=v).pack()
            elif type_ == 'choice':
                ttk.Combobox(f_,textvariable=v,values=['Jour','Nuit'],validate='key').pack(side='right')
            elif type_ == 'radio_bouton':
                Radiobutton(f_,text='OUI',variable=v,value='OUI',state='active' if v.get() == 'OUI' else 'normal').pack(side='left')
                Radiobutton(f_,text='NON',variable=v,value='NON', state = 'active' if v.get() == 'NON' else 'normal').pack(side='left')
            f_.pack(padx=5,pady=5)

        Button(f_dev,text='imprimantes',width=15,command=self.printer).pack()

        f_dev.pack()

        f_botton = Frame(self.window,background='skyblue')
        Button(f_botton,text='Annuler',command=self.quit).pack(side='right')
        Button(f_botton,text='Appliquer',command=self.save).pack(side='left')
        f_botton.pack(side=BOTTOM,padx=3)

    def quit(self):
        """Abbandon des modifications"""
        self.window.destroy()

    def printer(self):
        pass
    
    def save(self):
        """Enregistrement dans le fichier de configuration"""
        for name in self.list_var:
            setting.set(name,self.window.getvar(name))

        if setting.get('auto_login') == 'OUI':
            save_cookie()
        setting.save()
        self.window.destroy()

class Printer:
    def __init__(self,data):
        
        self.window = Toplevel(background='skyblue')
        self.window.geometry('720x520')
        self.window.resizable(False,False)
        self.data = data

        Label(self.window,text="Vente",font=('',24),width=24,background='skyblue').pack(side=TOP,padx=5,pady=5)

        f_dev = Frame(self.window,background='skyblue')
        for name , value in data.items():
            if name in ('marchandises') :
                continue
            f = Frame(f_dev,background='skyblue')
            Label(f,text=f"{name.capitalize()} : ",font=('',15)).pack(side='left')
            Label(f,text=value,font=('',15)).pack()
            f.pack(padx=3,pady=3)

        f8 = Frame(f_dev,height=100,width=155,background='skyblue')
        lc_temp = ttk.Treeview(f8,columns=('produit','quantite','prix'))#,height=50)
        lc_temp.heading('produit',text='Produits')
        lc_temp.column('produit',width=80)
        lc_temp.heading('quantite',text='Quantite')
        lc_temp.column('quantite',width=60)
        lc_temp.heading('prix',text='Prix')
        lc_temp.column('prix',width=80)
        lc_temp['show'] = 'headings'

        lc_temp.pack(fill=Y,expand=1)
        f8.pack()

        for prod, info in data.get('marchandises').items():
            lc_temp.insert('','end',value=(prod,info[0],info[1]))

        f_dev.pack()

        f_foot = Frame(self.window,background='skyblue')
        Button(f_foot,text='OK',width=5,command=self.close).pack(side='left')
        Button(f_foot,text='Imprimer',width=5,command=self.formantage).pack(side='left')
        f_foot.pack(side='bottom',padx=5,pady=5)
  
    def close(self):
        self.window.destroy()

    """def lister_imprimantes(self):
        name_imprimantes = []
        imprimantes = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        for i, imprimante in enumerate(imprimantes):
            name_imprimantes.append(imprimante[2])
        return imprimantes
    """
    def imprimer_pdf(self,fichier_pdf, nom_imprimante=None):
        raise NotImplementedError()
        """
        os.system(f"cp {fichier_pdf} /home/oem/Documents ")
        if os.name == 'posix':
            if subprocess.run(["lp", fichier_pdf]).returncode == 0:
                alert_wn("Le document a été envoyé à l'imprimante avec succès.")
            else:
                alert_wn("Erreur lors de l'envoi du document à l'imprimante.")
        elif os.name == 'nt':
            if nom_imprimante is None:
                nom_imprimante = win32print.GetDefaultPrinter()
            try:
                win32api.ShellExecute(0, "print", fichier_pdf, f'/d:"{nom_imprimante}"', ".", 0)
            except Exception as e:
                alert_wn(f"Erreur lors de l'impression : {e}")
        else:
            alert_wn("Le systeme d'exploitation n'est pas pris en charge")
    """

    def formantage(self):
        param = self.data
        param.update(setting.all())
        
        # Création du PDF en mémoire
        pdf_buffer = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)

        # Styles de texte
        styles = getSampleStyleSheet()
        style_normal = styles['Normal']
        style_heading = styles['Heading1']

        # Contenu du document
        content = []
        img_b64 = param.get('logo')
        if img_b64:
            img = base64.decodebytes(img_b64)
            f_image = tempfile.NamedTemporaryFile(delete=False)
            f_image.write(img)
            f_image.close()
            logo = rep_image(f_image.name,height=20,width=30)
            content.append(logo)
            content.append(Spacer(1,5))

        # Ajout de l'en-tête
        en_tete = Paragraph(param.get('boutique'), style_heading)
        content.append(en_tete)
        content.append(Spacer(1, 6))
        content.append(Paragraph(param.get('description'),style_heading))
        content.append(Spacer(1, 16))

        content.append(Paragraph(f"Ventes id : {param.get('vente_id')}",style_normal))
        content.append(Spacer(1, 6))
        content.append(Paragraph(f"Client : {param.get('client_id')}",style_normal))
        content.append(Spacer(1, 6))
        content.append(Paragraph(f"Vendeur : {param.get('vendeur')}",style_normal))
        content.append(Spacer(1, 6))
        content.append(Paragraph(f"Date : {param.get('date')}",style_normal))
        content.append(Spacer(1, 6))
        content.append(Paragraph(f"Prix : {param.get('prix')}",style_normal))
        content.append(Spacer(1, 10))

        # Ajout d'un tableau
        data = [['Produit', 'Quantite', 'Prix']]
        for prod, info in data.get('marchandises').items():
            data.append([prod , info[0], info[1]])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

        content.append(table)
        content.append(Spacer(1, 12))  # Espacement

        # Ajout de l'épilogue
        epilogue = Paragraph(param.get('contact'), style_normal)
        content.append(epilogue)

        # Génération du PDF dans le buffer
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        doc.build(content)

        # Fermeture du buffer pour s'assurer que tout est écrit
        pdf_buffer.close()

        self.imprimer_pdf(pdf_buffer.name)
        os.unlink(pdf_buffer.name)
        if img_b64:
            os.unlink(f_image.name)


setting = Config()
temp_setting = Config(temp_file=True)
version = '0.0.1a0'



