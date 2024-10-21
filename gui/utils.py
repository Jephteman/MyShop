from config import *
from tkinter import *

def alert_wn(message):
    f = Toplevel()
    f.title("Alert")
    f.geometry("550x100")
    f.resizable(False,False)
    Label(f,text=message,height=3,relief='solid',wraplength=540).pack()
    Button(f,text='OK',command=f.destroy).pack(side='bottom')

def login_wn():
    def check():
        data = {'username':u.get(),'password':p.get()}
        resp = client.API('')
        try:
            resp.connect(data)
            root.destroy()
        except Exception as e:
            alert_wn(e)

    root = Tk()
    u = StringVar()
    p = StringVar()
    root.title("Connection")
    root.resizable(False,False)
    Label(root,text="Connection au serveur",font=('',15),wraplength=540,padx=10,pady=10).pack()
    
    f1 = Frame(root,padx=8,pady=8)
    Label(f1,text="Nom d'utilisateur : ").pack(side='left')
    Entry(f1,textvariable=u).pack(side='right')
    f1.pack()

    f2 = Frame(root,padx=8,pady=8)
    Label(f2,text="Mot de passe   : ").pack(side='left')
    Entry(f2,textvariable=p,show='*').pack(side='right')
    f2.pack()

    Button(root,text='Connecter',command=check,padx=8,pady=8,width=15).pack()

    root.mainloop()

def about():
    f = Toplevel()
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
        self.list_wind = {0:self.setup0,1:self.setup1,2:self.setup2}
        self.etape = 0
        self.root = Tk(className="Installation MyShop (version)")
        self.root.geometry('720x520')
        self.root.resizable(height=False,width=False)

        # le frame rotatif , qui peu changer des text ou delement 
        self.p_frame = Frame(self.root,width=700,height=500,padx=10,pady=10)


        f_both = Frame(self.root)

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
        self.frame = Frame(self.p_frame,width=700,height=500,padx=10,pady=10)
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

        self.var_name = StringVar(self.root)
        self.var_url  = StringVar(self.root)

        self.frame = Frame(self.p_frame,padx=10,pady=10)
        Label(self.frame,font= ('',23) ,text="CONFIGURATION \n").pack(side='top')
        Label(self.frame,text="Veillez remplir ce formulaire ",font=('',12)).pack()

        f1 = Frame(self.frame)
        Label(f1,text="Nom de la boutique : ",height=3).pack(side='left')
        Entry(f1,textvariable=self.var_name).pack(side="right")
        f1.pack()
        f2  = Frame(self.frame)
        Label(f2,text="Url du serveur :  ",height=3).pack(side='left')
        Entry(f2,textvariable=self.var_url).pack(side="right")
        f2.pack()

        self.frame.pack()
        
    def install(self):
        config = ConfigParser()
        config['DEFAULT'] = {}
        config["DEFAULT"]['name'] = self.var_name.get()
        config['DEFAULT']['url'] = self.var_url.get()

        try:
            with pathlib.Path(os.getcwd()).joinpath('.config.txt').open('w') as f:
                config.write(f)
                f.close()

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


        self.frame = Frame(self.p_frame)
        Label(self.frame,font= ('',23) ,text="Resultat \n").pack(side='top')
        Label(self.frame,text=text,font=('',20)).pack()


        self.frame.pack()


