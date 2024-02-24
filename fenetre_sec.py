from tkinter import *
from tkinter import ttk
from functions import *
import posix
from json import JSONEncoder

def f_about(root):
    f = Toplevel(root)#,height=100,width=100)
    f.geometry('500x550')
    Label(f,text='\nCe programme a été developpé sous license GNU/Linux \n').pack()
    Label(f,text='Pour asurrer la gestion d\'une boutique ou quelque chose du genre ').pack()
    """Quelques ajout"""
    Label(f,text="Contact : Jephte Mangenda ( tech5industrie@gmail.com ) ").pack(side='bottom')
    Label(f,text="Disponible sur : https://github.com/Jephteman/MyShop").pack(side='bottom')
    Label(f,text="Version : version").pack(side='bottom')

def csv_import(root):
    f = Message(root)

"""Setup process"""
def setup0():
    """Message de bienvenu et un bref message """
    def next():
        root.destroy()
        setup1()

    root = Tk(className="Installation MyShop (version)")
    root.geometry('720x520')
    root.resizable(height=False,width=False)

    Label(root,text="\n BIENVENUE  ",height=10).pack()
    Label(root,text="""Ce programme a été concu pour faciliter la gestion d'une boutique \n 
          Il est completement libre et donc vous n'avez pas à vous souciez en ce qui concerne la license \n""").pack()
    Label(root,text=""" Ce programme à été ecrit par Jephte Mangenda ( tech5industrie@gmail.com ) et vous pouvez le retrouver sur \n Github ( https://github.com/Jephteman/MyShop )
""").pack()
    Label(root,text="\nNous allons commencer la configuration du programme").pack()
    Button(root,text="J'accepte et j'installe",bg='skyblue',command=next).pack(side='bottom')
    root.mainloop()

def setup1():
    """ Choix du type de stockage"""

    def next():
        root.destroy()
        setup2(choix.get())
    
    root = Tk(className="Etape 1")
    root.geometry('720x520')
    root.resizable(height=False,width=False)

    choix = StringVar(value='local')
    Label(root,height=5,text="CONFIGURATION DE LA BASE DE DONNÉE").pack(side='top')
    Label(root,text="Avant d'aller plus loin nous devons nous assurer du lieu de sauvegarde de vos donnée.").pack()
    Label(root,text='Ainsi vous êtes invité à fournir quelque directive').pack()
    Label(root,text="\nVoulez vous stocker vos données en Local ou Distant ? \n").pack()
    Radiobutton(root,variable=choix,text='Localement',value='local',state="active").pack()
    Radiobutton(root,variable=choix,text="A Distance",value='remove').pack()

    Button(root,text='Suivant',bg='skyblue',command=next).pack(side='bottom')

    root.mainloop()

def setup2(choix): # inachever , la fonction parcourir
    """Configuration de la db """
    data = database()
    def next():
        if choix == 'local':
            arg = {'db_name':'mylocaldb.db','path':d.get(),'name':name.get()}  
            if data.check(type='local',arg=arg):
                root.destroy()
                finish('local',arg=arg)
            else :
                alerte.set("Un probleme est survenu")
            
        else:
            arg = {'host':host.get(),'username':user.get(),'passwd':passwd.get(),'db_name':db_name.get(),'name':name.get()}
            if data.check('remove',arg):
                finish('remove',arg)
            else:
                alerte.set("Un probleme est survenu")


    def parcourir():
        pass


    root = Tk(className="Etape 2")
    root.geometry('720x520')
    root.resizable(height=False,width=False)

    alerte = StringVar()
    name = StringVar()

    if choix == 'local':
        d = StringVar()
        Label(root,height=5,text='Configuration de Base de donnée local \n').pack()
        Label(root,text="La configution d'une base de donnée local signifie que vos données seront stocker \n sur cette machine").pack()
        f = Frame(root)
        Label(f,text="Emplacement d'installation : ").pack(side='left')
        Entry(f,textvariable=d).pack(side="left")
        Button(f,text='Parcourir',command=parcourir).pack(side='right')
        f.pack()
        f1 = Frame(root)
        Label(f1,text="Nom de la boutique : ").pack(side='left')
        Entry(f1,textvariable=name).pack(side="left")
        f1.pack()

        Label(root,bg='red',textvariable=alerte).pack()
        Button(root,text="Suivant",command=next).pack(side='bottom',fill=Y)

    elif choix == 'remove':
        host = StringVar()
        user = StringVar()
        passwd = StringVar()
        db_name = StringVar()
        directory = StringVar()

        Label(root,height=5,text="Configuration de la BD distante \n").pack()
        Label(root,text="Ce programme ne prend en charge que MySQL comme base de donnée distante").pack()
        Label(root,text="Veillez entrez les identifiants de votre base de donnée MySQL \n").pack()
        f0 = Frame(root)
        Label(f0,text="Nom de la boutique : ").pack(side='left')
        Entry(f0,textvariable=name).pack(side="left")
        f0.pack()

        f1 = Frame(root)
        Label(f1,text="adress du server (IP , nom de domaine) : ").pack(side='left')
        Entry(f1,textvariable=host).pack(side='right')
        f1.pack()
        f2 = Frame(root)
        Label(f2,text="Username : ").pack(side='left')
        Entry(f2,textvariable=user).pack(side='right')
        f2.pack()
        f3 = Frame(root)
        Label(f3,text="Mot de pass").pack(side='left')
        Entry(f3,textvariable=passwd).pack(side='right')
        f3.pack()
        f4 = Frame(root)
        Label(f4,text="Nom de la BD : ").pack(side='left')
        Entry(f4,textvariable=db_name).pack(side='right')
        f5 = Frame(root)
        Label(f5,text="Emplacement d'installation : ").pack(side='left')
        Entry(f5,textvariable=directory).pack(side="left")
        Button(f5,text='Parcourir',command=parcourir).pack(side='right')
        f5.pack()

        Label(root,textvariable=alerte,bg='red').pack()

        Button(root,text='Suivant',bg='skyblue',command=next).pack(side='bottom')

    root.mainloop()

def finish(t,arg):
    """ finalisation de l'installation """
    def ok():
        root.destroy()
        exit()

    def success(a):
        data = JSONEncoder().encode(a)
        try :
            open('.config.txt','w').write(data)
            return True
        except:
            return False
        
    n = arg['name'] if 'name' in arg.keys() else ''
    p = arg['passwd'] if 'passwd' in arg.keys() else ''
    u = arg['username'] if 'username' in arg.keys() else ''
    h = arg['host'] if 'host' in arg.keys() else ''
    dname = arg['db_name'] if 'db_name' in arg.keys() else ''
    path = arg['path'] if 'path' in arg.keys() else ''

    config = {'type':t,'name':n,'username':u,'passwd':p,'host':h,'db_name':dname,'path':path}

    resp = success(config)

    root = Tk(className="Installation")
    root.geometry("500x500")
    root.resizable(height=False,width=False)

    Label(root,text="Résultat",height=5).pack()
    Label(root,text="Après toutes ces étapes nous sommes arrivé à la fin ",height=3).pack()
    if resp :
        Label(root,text="L'installation a eu lieu avec sucesss").pack()
        Label(root,text="Veillez redemarrer le programme").pack()
    else :
        Label(root,text="Une erreur a eu lien durant l'installation ").pack()
        Label(root,text="Veillez recommencer l'installation").pack()
    Button(root,text="OK",bg='skyblue',command=ok).pack(side='bottom')