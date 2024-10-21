from tkinter import *
from tkinter import ttk
from functions import *
import posix
from json import JSONEncoder

def f_about(root):
    f = Toplevel(root)#,height=100,width=100)
    f.geometry('500x550')
    f.resizable(width=False,height=False)
    Label(f,text='\nCe programme a été developpé sous license GNU/Linux \n').pack()
    Label(f,text='Pour asurrer la gestion d\'une boutique ou quelque chose du genre ').pack()
    """Quelques ajout"""
    Label(f,text="Contact : Jephte Mangenda ( tech5industrie@gmail.com ) ").pack(side='bottom')
    Label(f,text="Disponible sur : https://github.com/Jephteman/MyShop").pack(side='bottom')
    Label(f,text="Version : version").pack(side='bottom')

def csv_import(root):
    f = Message(root)

"""Setup process"""
class setup:
    def __init__(self):
        self.etape = 0
        self.error = False
        self.argument = {}
        self.root = Tk(className="Installation MyShop (version)")
        self.root.geometry('720x520')
        self.root.resizable(height=False,width=False)
        self.alert = StringVar()
        self.p_frame = Frame(self.root,width=700,height=500)
        self.frame = Frame(self.p_frame,width=700,height=500)
        Button(self.root,text="Suivant",command=self.next).pack(side='bottom')
        Label(self.root,bg='red',textvariable=self.alert).pack(side='bottom')
        self.setup0()
        self.p_frame.pack()
        self.root.mainloop()

    def setup0(self):
        """Message de bienvenu et un bref message """
        self.etape = 1
        Label(self.frame,text="\n BIENVENUE  ",height=10).pack()
        Label(self.frame,text="""Ce programme a été concu pour faciliter la gestion d'une boutique \n 
          Il est completement libre et donc vous n'avez pas à vous souciez en ce qui concerne la license \n""").pack()
        Label(self.frame,text=""" Ce programme à été ecrit par Jephte Mangenda ( tech5industrie@gmail.com ) et vous pouvez le retrouver sur \n Github ( https://github.com/Jephteman/MyShop )""").pack()
        Label(self.frame,text="\nNous allons commencer la configuration du programme").pack()
        self.frame.pack()

    def setup1(self):
        """ Choix du type de stockage"""
        self.etape = 2 
        self.frame = Frame(self.p_frame)
        self.argument['choix'] = StringVar(value='local')
        Label(self.frame,height=5,text="CONFIGURATION DE LA BASE DE DONNÉE").pack(side='top')
        Label(self.frame,text="Avant d'aller plus loin nous devons nous assurer du lieu de sauvegarde de vos donnée.").pack()
        Label(self.frame,text='Ainsi vous êtes invité à fournir quelque directive').pack()
        Label(self.frame,text="\nVoulez vous stocker vos données en Local ou Distant ? \n").pack()
        Radiobutton(self.frame,variable=self.argument['choix'],text='Localement',value='local',state="active").pack()
        Radiobutton(self.frame,variable=self.argument['choix'],text="A Distance",value='remove').pack()

        self.frame.pack()

    def setup2(self): 
        """Configuration de la db """
        self.etape = 3
        self.frame = Frame(self.p_frame)

        self.argument['name'] = StringVar()

        if self.argument['choix'].get() == 'local':
            self.argument['d'] = StringVar()
            Label(self.frame,height=5,text='Configuration de Base de donnée local \n').pack()
            Label(self.frame,text="La configution d'une base de donnée local signifie que vos données seront stocker \n sur cette machine").pack()
            f = Frame(self.frame)
            Label(f,text="Emplacement d'installation : ").pack(side='left')
            Entry(f,textvariable=self.argument['d']).pack(side="left")
            Button(f,text='Parcourir',command=self.parcourir).pack(side='right')
            f.pack()
            f1 = Frame(self.frame)
            Label(f1,text="Nom de la boutique : ").pack(side='left')
            Entry(f1,textvariable=self.argument['name']).pack(side="left")
            f1.pack()

        elif self.argument['choix'].get() == 'remove':
            self.argument['host'] = StringVar()
            self.argument['user'] = StringVar()
            self.argument['passwd'] = StringVar()
            self.argument['db_name'] = StringVar()
            self.argument['directory'] = StringVar()

            Label(self.frame,height=5,text="Configuration de la BD distante \n").pack()
            Label(self.frame,text="Ce programme ne prend en charge que MySQL comme base de donnée distante").pack()
            Label(self.frame,text="Veillez entrez les identifiants de votre base de donnée MySQL \n").pack()
            f0 = Frame(self.frame)
            Label(f0,text="Nom de la boutique : ").pack(side='left')
            Entry(f0,textvariable=self.argument['name']).pack(side="left")
            f0.pack()

            f1 = Frame(self.frame)
            Label(f1,text="adress du server (IP , nom de domaine) : ").pack(side='left')
            Entry(f1,textvariable=self.argument['host']).pack(side='right')
            f1.pack()
            f2 = Frame(self.frame)
            Label(f2,text="Username : ").pack(side='left')
            Entry(f2,textvariable=self.argument['user']).pack(side='right')
            f2.pack()
            f3 = Frame(self.frame)
            Label(f3,text="Mot de pass").pack(side='left')
            Entry(f3,textvariable=self.argument['passwd']).pack(side='right')
            f3.pack()
            f4 = Frame(self.frame)
            Label(f4,text="Nom de la BD : ").pack(side='left')
            Entry(f4,textvariable=self.argument['db_name']).pack(side='right')
            f4.pack()
            f5 = Frame(self.frame)
            Label(f5,text="Emplacement d'installation : ").pack(side='left')
            Entry(f5,textvariable=self.argument['directory']).pack(side="left")
            Button(f5,text='Parcourir',command=self.parcourir).pack(side='right')
            f5.pack()

        self.frame.pack()

    def finish(self):
        """ finalisation de l'installation """
        self.etape = 4
        self.frame = Frame(self.p_frame)

        def success(a):
            data = JSONEncoder().encode(a)
            try :
                open('.config.txt','w').write(data)
                self.error = False
                return True
            except:
                self.error = True
                self.alert.set("Nous n'avons pas pu enregistrer la configuration \n Veillez changer d'emplacement")
                
                return False
        
        n = self.argument['name'].get() if 'name' in self.argument.keys() else ''
        p = self.argument['passwd'].get() if 'passwd' in self.argument.keys() else ''
        u = self.argument['username'].get() if 'username' in self.argument.keys() else ''
        h = self.argument['host'].get() if 'host' in self.argument.keys() else ''
        t = self.argument['choix'].get() if 'choix' in self.argument.keys() else ''
        dname = self.argument['db_name'] if 'db_name' in self.argument.keys() else ''
        path = self.argument['path'] if 'path' in self.argument.keys() else ''

        config = {'type':t,'name':n,'username':u,'passwd':p,'host':h,'db_name':dname,'path':path}
        resp = success(config)

        Label(self.frame,text="Résultat",height=5).pack()
        Label(self.frame,text="Après toutes ces étapes nous sommes arrivé à la fin ",height=3).pack()
        if resp :
            Label(self.frame,text="L'installation a eu lieu avec sucesss").pack()
            Label(self.frame,text="Veillez redemarrer le programme").pack()
        else :
            Label(self.frame,text="Une erreur a eu lien durant l'installation ").pack()
            Label(self.frame,text="Veillez recommencer l'installation").pack()

        self.frame.pack()

    def next(self):
        if self.etape == 1:
            self.frame.destroy()
            self.setup1()
        elif self.etape == 2:
            self.frame.destroy()
            self.setup2()
        elif self.etape == 3:
            data = database()
            if self.argument['choix'].get() == 'local':
                arg = {'db_name':'mylocaldb.db','path':self.argument['d'].get(),'name':self.argument['name'].get()}  
                if data.check('local',arg=arg):
                    self.frame.destroy()
                    self.finish()
                else : 
                    self.alert.set("Nous n'avons pas pû nous connecter à la base de donnée")
            
            else:
                arg = {'host':self.argument['host'].get(),'username':self.argument['user'].get(),'passwd':self.argument['passwd'].get(),'db_name':self.argument['db_name'].get(),'name':self.argument['name'].get()}
                if data.check('remove',arg):
                    self.frame.destroy()
                    self.finish()
                else:
                    self.alert.set("Nous n'avons pas pû nous connecter à la base de donnée")
        elif self.etape == 4:
            self.root.destroy()
            exit(0)
    def parcourir(self):
        pass