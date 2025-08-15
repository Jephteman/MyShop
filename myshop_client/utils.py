from .client import API
from .widgets import *

from tkinter.filedialog import askopenfilename, asksaveasfile
from configparser import ConfigParser
from json import JSONDecoder , JSONEncoder

import os, subprocess
import csv
import base64
import platform
import pathlib
import tempfile
import datetime
import matplotlib.pyplot as plt 
from PIL import Image, ImageTk

from reportlab.lib.pagesizes import HALF_LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image as rep_Image
from reportlab.lib import colors

import pkg_resources


try:
    import pywin32_system32 as win32 # type: ignore
except:
    if os.name == 'nt':
        print("Vous ne pourrez pas effectuer d'impression puis que vous n'avez installé 'win32print'")


class Config:
    def __init__(self,temp_file=False):
        self.temp_file = temp_file
        self.config = ConfigParser(allow_no_value=True)
        self.filename = ''
        self.config_dir = ''
        
        if not temp_file:
            if platform.system() == "Windows":
                self.config_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "myshop")
            else:
                self.config_dir = os.path.expanduser("~/.config/myshop")

            self.filename = os.path.join(self.config_dir, "config.txt")
            self.conf_file = pathlib.Path(self.filename)
            self.config.read(self.conf_file)
            
        self.cookie = {}
        
    def reload(self):
        self.config.read(self.conf_file)
    
    def is_installed(self):
        return True if self.get('url') != '' else False

    def save(self):
        if self.temp_file:
            raise Exception("Fichier temporaire ne peut etre stocker")
        with open(self.conf_file,'w') as f:
            self.config.write(f)
            alert_wn("Paramtres sauvegarder avec success")

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

def askfile_save(var,file_type): # il ne fonctionne plus, nous ne lui renvoyons plus var
    x = asksaveasfile(filetypes=file_type)
    if x:
        var.set(x.name)
        x.close()

def askfile_open(var,file_type): # il ne fonctionne plus, nous ne lui renvoyons plus var
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

class LoginPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        # Création des différentes frames
        for F in (self.LoginFrame,):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        temp_setting.set('is_login','no')
        cookie = setting.get('cookie')
        if (setting.get('auto_login') == 'OUI') and cookie:
            setting.update_cookie()
            is_valid = API(setting.get('url'),'',cookie=setting.cookie).check_cookie()
            if is_valid:
                self.islogin(is_valid)
            else:
                self.show_frame('LoginFrame')
        else:
            self.show_frame('LoginFrame')
            
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        frame.tkraise()
        
    def LoginFrame(self,contenair):
        def check():
            data = {'username':frame.getvar('username'),'password':frame.getvar('password')}
            resp = API(setting.get('url'),'')
            try:
                config_serv = resp.connect(data)
                self.islogin(config_serv)
            except Exception as e:
                alert_wn(e)
            
        frame = Frame(contenair,background='skyblue')
        u = StringVar(frame,name='username')
        p = StringVar(frame,name='password')
        Label(frame,text="Connection au serveur",font=('',15),wraplength=540,padx=10,pady=10,background='skyblue').pack()
        
        img_name = setting.get('logo')
        if img_name and pathlib.Path(img_name).exists():
            img_file = img_name
        else:
            try:
                img_file = pkg_resources.resource_filename('myshop','myshop_client/logo.gif')
            except ModuleNotFoundError:
                img_file = pathlib.Path(__file__).parent.joinpath('logo.png')
            except Exception as e:
                alert_wn(e)

        img = Image.open(img_file)
        photo = ImageTk.PhotoImage(img)
        
        Label(frame,image=photo).pack(padx=5,pady=5)
        f1 = Frame(frame,padx=8,pady=8,background='skyblue')
        PlaceholderEntry(f1,textvariable=u,placeholder="Nom d'utilisateur").pack()
        PlaceholderEntry(f1,textvariable=p,placeholder="Mot de passe",show='*').pack()
        f1.pack()

        Button(frame,text='Connecter',command=check,padx=8,pady=8,width=15).pack()
        
        Button(frame,text='Parametre',command=lambda: self.controller.show_frame('ParametrePage'),padx=8,pady=8,width=15).pack(side='right')
        

        return frame
        
    def islogin(self,config_serv):
        for label, value in config_serv.items():
            if type(value) is dict:
                value = JSONEncoder().encode(value)
            if value == None:
                value = ''
            temp_setting.set(label,value)
            
        temp_setting.set('is_login','yes')
        temp_setting.update_cookie()
        self.controller.show_frame('VentePage')
        self.controller.islogin()

class AboutPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
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
            
        self.show_frame('Home')
        
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        frame.tkraise()
        
    def Home(self,container):
        frame = Frame(container,background='skyblue')
        Label(frame,text='\nCe programme a été developpé sous license GNU/Linux \n',background='skyblue').pack()
        Label(frame,text='Pour asurrer la gestion d\'une boutique ou quelque chose du genre ',background='skyblue').pack()
        
        try:
            img_file = pkg_resources.resource_filename('myshop','myshop_client/logo.gif')
        except ModuleNotFoundError:
            img_file = pathlib.Path(__file__).parent.joinpath('logo.gif')

        img = Image.open(img_file)
        photo = ImageTk.PhotoImage(img)
        Label(frame,image=photo).pack(padx=5,pady=5)
        """Quelques ajout"""
        Label(frame,text="Contact : Jephte Mangenda ( tech5industrie@gmail.com ) ",background='skyblue').pack(side='bottom')
        Label(frame,text="Disponible sur : https://github.com/Jephteman/MyShop",background='skyblue').pack(side='bottom')
        Label(frame,text=f"Version : {version}",background='skyblue').pack(side='bottom')
        
        return frame

def save_cookie(): # save cookie in permenante setting
    setting.set('cookie',temp_setting.get('cookie'))

def clean_variable(frame):
    """Reinitialise les valeurs des varibles """
    for child in frame.winfo_children():
        if 'variable' in child.keys() or  'textvariable' in child.keys():
            if 'variable' in child.keys():
                var = child['variable']
            else:
                var = child['textvariable']
            frame.setvar(str(var),'')
        elif isinstance(child,Text):
            child.delete('1.0',END)
            
        elif hasattr(child,'winfo_children'):
            clean_variable(child)

def selecteur_date(variable_name,frame_object):#,entry_object):
    """Fenetre pour permettre à l'utilisateur de fournir la date """
    def fermeture():
        frame_object.focus_set()
        win.destroy()
        
    def valider_date():
        jour = frame.nametowidget('frame_jour.spin_jour').get()
        mois = frame.nametowidget('frame_mois.spin_mois').get()
        annee = frame.nametowidget('frame_annee.spin_annee').get()
        frame_object.setvar(variable_name,f"{jour}/{mois}/{annee}")
        frame_object.focus_set()
        win.destroy()
        
    win = Toplevel()
    win.resizable(False,False)
    win.title("Sélecteur de date")
    win.geometry("390x180")
    win.protocol('WM_DELETE_WINDOW',fermeture)

    # Cadre pour les sélecteurs
    frame = ttk.Frame(win,padding="10")
    frame.pack(fill='both', expand=True)
    models = [
        {'name':'jour','label':'Jour:    ','from':1,'to':31,'default':datetime.datetime.now().day},
        {'name':'mois','label':'Mois:   ','from':1,'to':12,'default':datetime.datetime.now().month},
        {'name':'annee','label':'Année: ','from':1900,'to':2100,'default':datetime.datetime.now().year}
    ]

    for data in models:
        frame_in = Frame(frame,name=f"frame_{data.get('name')}")
        ttk.Label(frame_in, text=data.get('label'),background='skyblue').pack(side='left')
        spin_jour = ttk.Spinbox(frame_in, from_=data.get('from'), to=data.get('to'), width=5,name=f"spin_{data.get('name')}")
        spin_jour.pack(side='right',padx=5, pady=5)
        spin_jour.set(data.get('default'))
        frame_in.pack()

    # Bouton de validation
    btn_valider = ttk.Button(frame, text="Valider", command=valider_date)
    btn_valider.pack(pady=10,side='bottom')


"""Setup process"""
class SetupPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.etape = 0
        
        container = Frame(self,background='skyblue',name='main_frame')
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        
        # Création des différentes frames
        for F in (self.Page0, self.Page1, self.Page2):
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid(row=0, column=0, sticky="nsew")
            
        f_both = Frame(self,background='skyblue',name='frame_botton')
        b_prev = Button(f_both,text="Precedent",command=self.prev,name='b_prev_button')
        b_prev.pack(side="left")
        b_next = Button(f_both,text="Suivant",command=self.next,name='b_next_button')
        b_next.pack(side='left')
        b_fin = Button(f_both,text="Terminer",name='b_fin_button',command=lambda: controller.show_frame('LoginPage'),state='disabled')
        b_fin.pack(side='left')
        f_both.pack(side='bottom') # j dois trouver une autre facon de faire
        
        # Afficher la première frame
        self.show_frame("Page0")
    
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        if cont == 'Page0':
            b_prev = self.nametowidget('frame_botton.b_prev_button')
            b_prev.configure(state='disabled')
        if cont == 'Page2':
            self.install()
            b_prev = self.nametowidget('frame_botton.b_prev_button')
            b_prev.configure(state='active')
            
        frame.tkraise()
    
    def next(self):
        self.etape += 1
        self.show_frame(f'Page{self.etape}')
        
    def prev(self):
        self.etape -= 1
        self.show_frame(f'Page{self.etape}')

    def Page0(self,container):
        frame = Frame(container,background='skyblue',name='page1_frame')
        Label(frame,text="\n BIENVENU \n",font=('',21),background='skyblue').pack()
        text = """
            Ce programme a été concu pour faciliter la gestion d'une boutique  \n
            Ce programme à été ecrit par Jephte Mangenda ( tech5industrie@gmail.com )
            Vous pouvez le retrouver sur \n Github ( https://github.com/Jephteman/MyShop )
            Nous allons commencer la configuration du programme
            """
        Label(frame,text=text,font=('',11),background='skyblue').pack()
        return frame

    def Page1(self,container):
        """ Choix du type de stockage"""

        frame = Frame(container,background='skyblue')
        Label(frame,font= ('',23) ,text="CONFIGURATION \n",background='skyblue').pack(side='top')
        Label(frame,text="Veillez remplir ce formulaire ",font=('',12),background='skyblue').pack(padx=5,pady=5)

        f1 = Frame(frame,background='skyblue')
        StringVar(self,name='url')
        Label(f1,text=f"Url du serveur : ",background='skyblue').pack(side='left')
        Entry(f1,textvariable='url').pack(side="right")
        f1.pack(padx=3,pady=3)

        f1 = Frame(frame,background='skyblue')
        StringVar(self,name='proxy')
        Label(f1,text=f"Proxy : ",background='skyblue').pack(side='left')
        Entry(f1,textvariable='proxy').pack(side="right")
        f1.pack(padx=3,pady=3)

        # f1 = Frame(frame,background='skyblue')
        # StringVar(self,name='theme')
        # Label(f1,text=f"Theme : ",height=3).pack(side='left')
        # ttk.Combobox(f1,textvariable='theme',values=['Jour','Nuit'],validate='focusin',).pack(side='right')
        # f1.pack()

        f1 = Frame(frame,background='skyblue')
        StringVar(self,name='login_auto')
        Label(f1,text=f"Connection automatique : ",background='skyblue').pack(side='left')
        Radiobutton(f1,text='OUI',variable='auto_login',value='OUI',background='skyblue').pack(side='right')
        Radiobutton(f1,text='NON',variable='auto_login',value='NON',state='active',background='skyblue').pack(side='right')
        f1.pack(padx=3,pady=3)
                
        return frame
        
    def Page2(self,container):
        """ Choix du type de stockage"""
        StringVar(self,name='resultat')

        frame = Frame(container,background='skyblue')
        Label(frame,font= ('',23) ,text=" Resultat \n",background='skyblue').pack(side='top')
        Label(frame,textvariable='resultat',font=('',20),background='skyblue').pack()

        return frame
        
    def install(self):
        if not setting.config.has_section('CLIENT'):
            setting.config['CLIENT'] = {}
        
        setting.config['CLIENT']['url'] = self.getvar('url')
        setting.config['CLIENT']['proxy'] = self.getvar('proxy')
        setting.config['CLIENT']['auto_login'] = self.getvar('auto_login')
        #setting['CLIENT']['theme'] = self.getvar('theme')

        try:
            setting.save()
        except Exception as e:
            alert_wn(e)
            self.setvar('resultat',"L'installation a echoué. Veillez recommencer")
        else:
            b_next = self.nametowidget('frame_botton.b_next_button')
            b_prev = self.nametowidget('frame_botton.b_prev_button')
            b_fin = self.nametowidget('frame_botton.b_fin_button')
            self.setvar('resultat',"L'installation a reussi avec success.")
            b_next.configure(state='disabled')
            b_prev.configure(state='disabled')
            b_fin.configure(state='active')

class NotePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.notes = {}
        
        # Conteneur principal
        container = Frame(self,background='skyblue')
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
        
        if cont != 'Home':
            clean_variable(frame)
            # frame.setvar(name='var_author',value='')
            t = self.frames['Add'].nametowidget('wigdet_contenu')
            #t.delete('1.0',END)
            if action:
                try:
                    tableau = self.frames['Home'].nametowidget('body.tableau')
                    id_ = tableau.selection()[0]
                    data = self.notes.get(id_)
                    
                    self.frames['Add'].nametowidget('bottom.send_btn').config(state='disabled')
                except Exception as e:
                    alert_wn(e)
                    return 
                else:
                    frame.setvar(name='var_author',value=data.get('username'))
                    frame.setvar(name='var_sujet',value=data.get('sujet'))
                    t.insert('1.0',data.get('description'))
            else:
                self.frames['Add'].nametowidget('bottom.send_btn').config(state='active')
                
        frame.tkraise()
        
    def Home(self,contenair):
        frame = Frame(contenair,name='frame_home',background='skyblue')
        frame.bind('<Control-A>' or '<Control-a>',self.actualise)
        Label(frame,text='Notes',padx=5,pady=5,font=('',13),background='skyblue').pack()
        
        f1 = Frame(frame,padx=3,pady=3,background='skyblue',name='body')
        tab = ttk.Treeview(f1,columns=('id','sujet','user','date'),name='tableau')#,height=30)  # frame.nametowidget('tableau') # frame.insert
        tab.heading('id',text="Id")
        tab.heading('sujet',text="Sujet")
        tab.heading('user',text="Utilisateur")
        tab.heading('date',text="Date")

        tab['show'] = 'headings'

        sc = Scrollbar(f1,command=tab.yview)
        sc.pack(side="right",fill=Y)

        tab.configure(yscrollcommand=sc.set)
        
        tab.pack(fill="both", expand=True,pady=5,padx=5)

        f1.pack(fill="both", expand=True,pady=5,padx=5)

        f2 = Frame(frame,background='skyblue',name='bottom')

        Button(f2,text='Ajouter',padx=4,pady=4,command=lambda : self.show_frame('Add'),width=10).pack(side='left')
        Button(f2,text='Voir',padx=4,pady=4,command=lambda : self.show_frame('Add',action="see"),width=10).pack(side='left')
        Button(f2,text='Supprimer',padx=4,pady=4,command=self.delete,width=10).pack(side='right')

        f2.pack(side='bottom')
            
        return frame
        
    def Add(self,container):
        def ret():
            sujet = frame.tk.globalgetvar('var_sujet')
            contenu = frame.nametowidget('wigdet_contenu')
            param = {
                'sujet': sujet,
                'description' : contenu.get('1.0','end-1c')
            }
            try:
                api = API(setting.get('url'),'notes',cookie=temp_setting.cookie)
                d = api.add(param)
            except Exception  as e:
                alert_wn(e)
            else:
                d['username'] = temp_setting.get('username')
                n_id = str(d.get('note_id'))
                self.notes.update({n_id:d}),
                p = (n_id,d.get('sujet'),d.get('username'),d.get('date'))
                tab = self.frames['Home'].nametowidget('body.tableau')
                tab.insert('','end',iid=n_id,values=p)
                self.show_frame('Home')
                var_sujet.set('')
                
        
        frame = Frame(container,name='frame_add',background='skyblue')

        var_sujet = StringVar(frame,name='var_sujet')

        f1 = Frame(frame,padx=5,pady=5,background='skyblue',name='top')
        PlaceholderEntry(f1,textvariable=var_sujet,placeholder='Sujet').pack()
        f1.pack()

        #f3 = Frame(frame,background='skyblue',name='middle')
        Label(frame,text='Contenu : ',background='skyblue').pack()#side='left')
        var_contenu = Text(frame,name='wigdet_contenu',width=30,height=15)
        var_contenu.pack(fill="both", expand=True,pady=5,padx=5)#side='right')
        #f3.pack()
        
        f4 = Frame(frame,name='bottom',background='skyblue')
        Button(f4,text='Envoyer',width=10,padx=5,pady=5,command=ret,name='send_btn').pack(side='left')
        Button(f4,text='Annuler',width=10,padx=5,pady=5,command=lambda: self.show_frame('Home')).pack(side='right')
        f4.pack(side='bottom')
        
        return frame

    def actualise(self):
        tab = self.frames['Home'].nametowidget('body.tableau')
        try:
            api = API(setting.get('url'),'notes',cookie=temp_setting.cookie)
            self.notes.update(api.all())
        except Exception as e:
            alert_wn(e)
        
        for i , data in self.notes.items():
            n_id = str(data.get('note_id'))
            p = (n_id,data.get('sujet'),data.get('username'),data.get('date'))
            if not tab.exists(int(n_id)):
                tab.insert('','end',iid=n_id,values=p)

    def delete(self):
        try:
            tab = self.frames['Home'].nametowidget('body.tableau')
            id_ = tab.selection()[0]
            api = API(setting.get('url'),'notes',cookie=temp_setting.cookie)
            api.delete(id_)
            
            tab.delete(id_)
            self.notes.pop(id_)
        except Exception as e:
            alert_wn(e)

class NoticePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.notifications = {}
        
        # Conteneur principal
        container = Frame(self,background='skyblue')
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
        
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        frame.tkraise()
        
    def Home(self,contenair):
        frame = Frame(contenair,name='frame_home',background='skyblue')
        frame.bind('<Control-A>' or '<Control-a>',self.actualise)
        Label(frame,text='Notifications',padx=5,pady=5,font=('',13),background='skyblue').pack()
        
        f1 = Frame(frame,padx=3,pady=3,background='skyblue',name='body')
        tab = ttk.Treeview(f1,columns=('id','message','niveau','date'),name='tableau')#,height=30)  # frame.nametowidget('tableau') # frame.insert
        tab.heading('id',text="Id")
        tab.heading('message',text="Message")
        tab.heading('niveau',text="Niveau")
        tab.heading('date',text="Date")

        tab['show'] = 'headings'

        sc = Scrollbar(f1,command=tab.yview)
        sc.pack(side="right",fill=Y)

        tab.configure(yscrollcommand=sc.set)
        
        tab.pack(fill="both", expand=True,pady=5,padx=5)

        f1.pack(fill="both", expand=True,pady=5,padx=5)

        f2 = Frame(frame,background='skyblue',name='bottom')

        #Button(f2,text='Voir',padx=4,pady=4,command=lambda : self.show_frame('See'),width=10).pack(side='left')
        Button(f2,text='Supprimer',padx=4,pady=4,command=self.delete,width=10).pack(side='right')

        f2.pack(side='bottom')
            
        return frame

    def actualise(self):
        tab = self.frames['Home'].nametowidget('body.tableau')
        try:
            api = API(setting.get('url'),'notifications',cookie=temp_setting.cookie)
            self.notes.update(api.all())
        except Exception as e:
            alert_wn(e)
        
        for i , data in self.notifications.items():
            n_id = str(data.get('notification_id'))
            p = (n_id,data.get('message'),data.get('niveau'),data.get('date'))
            if not tab.exists(int(n_id)):
                tab.insert('','end',iid=n_id,values=p)

    def delete(self):
        try:
            tab = self.frames['Home'].nametowidget('body.tableau')
            id_ = tab.selection()[0]
            api = API(setting.get('url'),'notifications',cookie=temp_setting.cookie)
            api.delete(id_)
            
            tab.delete(id_)
            self.notifications.pop(id_)
        except Exception as e:
            alert_wn(e)

class Graphique:
    def __init__(self):
        def set_file():
            file_t = [('File text','*.pdf')]
            askfile_save(self.path,file_t)

        self.window = Toplevel(width=500,padx=5,pady=5,background='skyblue')
        self.window.title('Graphique')
        self.window.resizable(False,False)
        
        # en-tete  
        self.origine = StringVar(name='var_origine')
        self.fin = StringVar(name='var_fin')
        self.path = StringVar(name='var_path')
        self.type_ = StringVar(name='var_type')
        self.diag_form = StringVar(name='var_diag_form')
        graphic_type = (
            'date2n_vente',
            'client2n_vente',
            'produit2n_vente',
            'vendeur2n_vente'
        )
        diagram_type = (
            'baton',
            'circulaire',
            'courbe'
        )

        Label(self.window,text="Graphique",font=('',15),background='skyblue').pack()

        f1 = Frame(self.window,padx=15,pady=15,background='skyblue')
        Label(f1,text="Type : ",padx=8,font=('',15),background='skyblue').pack(side='left')
        ttk.Combobox(f1,textvariable=self.type_,values=graphic_type,validate='focusin').pack(side='right')
        f1.pack()

        f2 = Frame(self.window,padx=15,pady=15,background='skyblue')
        Label(f2,text="Diagramme : ",padx=8,font=('',15),background='skyblue').pack(side='left')
        ttk.Combobox(f2,textvariable=self.diag_form,values=diagram_type,validate='focusin').pack(side='right')
        f2.pack()


        f1 = Frame(self.window,background='skyblue')
        entry1 = PlaceholderEntry(f1,textvariable=self.origine,placeholder='A partir du ')
        entry1.bind('<FocusIn>', lambda event: selecteur_date('var_origine',self.window)) 
        entry1.pack(side='left')
        
        entry2 = PlaceholderEntry(f1,textvariable=self.fin, placeholder='Au')
        entry2.bind('<FocusIn>', lambda event: selecteur_date('var_fin',self.window)) 
        entry2.pack(side='right')
        f1.pack()

        f2 = Frame(self.window,background='skyblue')
        Label(f2,text='Emplacement : ',background='skyblue').pack(side='left')
        Entry(f2,textvariable=self.path,state='readonly').pack(side='left')
        Button(f2,text='parcourir',command=set_file,background='skyblue').pack(side='right')

        f2.pack()

        Button(self.window,text="Generer",command=self.find).pack(side='bottom')

    def find(self):
        try:
            from_ = self.origine.get()
            to = self.fin.get()

            param = None
            if from_ and to:
                param = {'from':from_,'to':to,"isform":True,'graphe_fonction':self.type_.get()}

            api = API(setting.get('url'),'graphiques',cookie=temp_setting.cookie)
            data_raw = api.all(param=param)
        except IndentationError as e:
            alert_wn(e)
        else:                        
            file_save = self.path.get()
            diagram_type = self.diag_form.get()
            if diagram_type == 'circulaire':
                plt.pie(data_raw.values(),label=data_raw.keys())
            elif diagram_type == 'baton':
                plt.bar(data_raw.keys(),data_raw.values())
            else: # dans le cas des courbes
                xlabel = self.type_.get().capitalize().split(sep='2')[0]
                plt.plot(data_raw.keys(),data_raw.values())
                plt.xlabel(xlabel)
                plt.ylabel("Nombres de vente")
            
            plt.title("Graphique des ventes")
            #plt.gcf().autofmt_xdate()

            try:
                plt.savefig(file_save,format='pdf',bbox_inches='tight',)
            except Exception as e :
                alert_wn("Une ereur s'est produite")
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
        Label(win,text='Exportation des donnees',font=('',17),padx=5,pady=5,background='skyblue').pack()

        f1 = Frame(win,background='skyblue')
        Label(f1,text='Ressource : ',background='skyblue').pack(side='left')
        ttk.Combobox(f1,textvariable=self.res,values=('ventes','logs','arrivages','produits','notes','sessions')).pack(side='right')
        f1.pack()

        f2 = Frame(win,background='skyblue')
        entry1 = PlaceholderEntry(f2,textvariable=self.origine,placeholder='A partir du ')
        entry1.bind('<FocusIn>', lambda event: selecteur_date(self.origine,f1,entry1)) 
        entry1.pack(side='left')
        
        entry2 = PlaceholderEntry(f2,textvariable=self.fin, placeholder='Au')
        entry2.bind('<FocusIn>', lambda event: selecteur_date(self.fin,f2,entry2)) 
        entry2.pack(side='right')
        f2.pack()
        
        f3 = Frame(win,background='skyblue')
        Label(f3,text='Emplacement : ',background='skyblue').pack(side='left')
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
            serilise_data = data.values()

            csv_file = self.path.get()
            if not serilise_data:
                alert_wn("Aucune donnee n'est disponible")
                return
            
            with open(csv_file,'w',newline='') as file:
                writer = csv.DictWriter(file,fieldnames=serilise_data[0].keys())
                writer.writeheader()
                writer.writerows(serilise_data)
            alert_wn('Donnees exportees avec success')

class ParametrePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        # Conteneur principal
        container = Frame(self,background='skyblue')
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        
        self.list_var = {
            'url':'str','proxy':'str',
            #'theme':'choice',
            #'auto_login':'radio_bouton'
            }
        
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
        Label(frame,text='Parametre',font=('',24),background='skyblue').pack(padx=5,pady=5)
        f_dev = Frame(frame,background='skyblue',name='body')

        for i, type_ in self.list_var.items():
            v = StringVar(frame,name=i)
            f_ = Frame(f_dev,background='skyblue')
            Label(f_,text=f'{i.capitalize()} : ',background='skyblue').pack(side='left')
            if type_ == 'str':
                Entry(f_,textvariable=v).pack()
            elif type_ == 'radio_bouton':
                Radiobutton(f_,text='OUI',variable=v,value='OUI').pack(side='left')
                Radiobutton(f_,text='NON',variable=v,value='NON').pack(side='left')
            f_.pack(padx=5,pady=5)

        #Button(f_dev,text='imprimantes',width=15,command=lambda : self.printer).pack()

        f_dev.pack()

        f_botton = Frame(frame,background='skyblue')
        Button(f_botton,text='Annuler',command=self.quit).pack(side='right')
        Button(f_botton,text='Appliquer',command=self.save).pack(side='left')
        f_botton.pack(side=BOTTOM,padx=3)
        
        return frame
        
    def actualise(self):
        frame = self.frames['Home']
        for name, nothing in self.list_var.items():
            value = setting.get(name)
          
            frame.setvar(name,value)
        
    def quit(self):
        """Abbandon des modifications"""
        if temp_setting.get('islogin') == 'yes':
            self.controller.show_frame('VentePage')
        else:
            self.controller.show_frame('LoginPage')

    def printer(self):
        pass
    
    def save(self):
        """Enregistrement dans le fichier de configuration"""
        for name in self.list_var:
            frame = self.frames['Home']
            value = frame.tk.globalgetvar(name)
            setting.set(name,value)

        if setting.get('auto_login') == 'OUI':
            save_cookie()
        setting.save()
        self.quit()

class Printer:
    def __init__(self,data):
        
        self.window = Toplevel(background='skyblue')
        self.window.geometry('720x520')
        self.window.resizable(False,False)
        self.data = data

        Label(self.window,text="Facture",font=('',24),width=24,background='skyblue').pack(side=TOP,padx=5,pady=5)

        f_dev = Frame(self.window,background='skyblue')
        
        for name , value in data.items():
            if name in ('marchandises') :
                continue
            f = Frame(f_dev,background='skyblue')
            Label(f,text=f"{name.capitalize()} : ",font=('',15),background='skyblue').pack(side='left')
            Label(f,text=value,font=('',15),background='skyblue').pack()
            f.pack(padx=3,pady=3)

        f8 = Frame(f_dev,background='skyblue')
        lc_temp = ttk.Treeview(f8,columns=('produit','quantite','prix'))#,height=50)
        lc_temp.heading('produit',text='Produits')
        lc_temp.column('produit',width=80)
        lc_temp.heading('quantite',text='Quantite')
        lc_temp.column('quantite',width=60)
        lc_temp.heading('prix_initial',text='Prix Unité')
        lc_temp.column('prix_initial',width=80)
        lc_temp.heading('prix_total',text='Total')
        lc_temp.column('prix_total',width=80)
        lc_temp['show'] = 'headings'

        lc_temp.pack(fill='both',expand=True)
        f8.pack(fill='both',expand=True)

        for prod, info in data.get('marchandises').items():
            lc_temp.insert('','end',value=(prod,info[0],info[1],info[2]))

        f_dev.pack()

        f_foot = Frame(self.window,background='skyblue')
        Button(f_foot,text='OK',width=5,command=lambda : self.close()).pack(side='left')
        Button(f_foot,text='Imprimer',width=5,command=lambda : self.formantage()).pack(side='left')
        f_foot.pack(side='bottom',padx=5,pady=5)
  
    def close(self):
        self.window.destroy()
        
    def imprimer_pdf(self,fichier_pdf, nom_imprimante=None):
        if os.name == 'posix':
            if subprocess.run(["lp", fichier_pdf.name]).returncode == 0:
                alert_wn("Le document a été envoyé à l'imprimante avec succès.")
            else:
                alert_wn("Erreur lors de l'envoi du document à l'imprimante.")
        elif os.name == 'nt':
            if nom_imprimante is None:
                nom_imprimante = win32print.GetDefaultPrinter()
            try:
                win32api.ShellExecute(0, "print", fichier_pdf.name, f'/d:"{nom_imprimante}"', ".", 0)
            except Exception as e:
                alert_wn(f"Erreur lors de l'impression : {e}")
        else:
            alert_wn("Le systeme d'exploitation n'est pas pris en charge")
            
        fichier_pdf.close()

    def formantage(self):
        param = self.data
        param.update(temp_setting.all())
        
        pdf_filename = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)

        
        doc = SimpleDocTemplate(pdf_filename.name,pagesize=HALF_LETTER,leftMargin=10 * mm,rightMargin=10 * mm,topMargin=5 * mm)

        # Styles personnalisés
        styles = getSampleStyleSheet()
        style_centered = ParagraphStyle(
            "Centered",
            parent=styles["Normal"],
            alignment=1,  # Centré
            fontSize=10,
            spaceAfter=6,
        )
        style_bold = ParagraphStyle("Bold",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=10)
        style_normal = styles["Normal"] 
        # Contenu de la facture
        story = []
        logo_path = param.get('logo')
        if logo_path:
            # 1. Logo (en-tête)
            logo = rep_Image(logo_path, width=50 * mm, height=30 * mm)  # Ajustez la taille
            logo.hAlign = "CENTER"
            story.append(logo)
            story.append(Spacer(1, 10))  # Espace après le logo

        # 2. Infos boutique
        story.append(Paragraph(param.get("boutique"), style_bold))
        story.append(Paragraph(param.get("address"), style_centered))
        story.append(Paragraph(param.get("telephone"), style_centered))
        story.append(Spacer(1, 10))

        # 3. Infos client (cadre gris)
        client_data = [
            [Paragraph(f"Client : {param.get('client_id')}", style_bold)],
            [Paragraph(f"Date : {param.get('date')}", style_normal)],
            [Paragraph(f"Facture : {param.get('vente_id')}", style_normal)],
        ]
        client_table = Table(client_data, colWidths=[80 * mm])
        client_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(client_table)
        story.append(Spacer(1, 10))

        # 4. Tableau des articles
        data = [['Produit','Qte','Prix Unité','Total']]
        for prod, info in param.get('marchandises').items():
            data.append([prod , info[0], info[1],info[2]])

        table = Table(data, colWidths=[50 * mm, 15 * mm, 25 * mm, 25 * mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 10))

        # 5. Totaux
        story.append(Paragraph(f"<b>TOTAL: {param.get('prix')}</b>", style_bold))
        story.append(Spacer(1, 15))

        # 6. Pied de page
        story.append(Paragraph(f"{param.get('remerciement')}", style_centered))

        # Génération du PDF
        doc.build(story)
        
        self.imprimer_pdf(pdf_filename)

setting = Config()
temp_setting = Config(temp_file=True)
version = '0.0.1a0'



