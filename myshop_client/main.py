import tkinter as tk
from .fenetres import *
from .gestion import *
from .admin_windows import *
from .utils import *

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        img_file = setting.get('logo')
        
        if not img_file or not pathlib.Path(img_file).exists():
            img_file = pkg_resources.resource_filename('myshop_client','logo.gif')
            
        img = Image.open((img_file))
        photo = ImageTk.PhotoImage(img)
        self.iconphoto(False,photo)
        
        # Conteneur principal
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        
        # Création des différentes frames
        for F in (MainPage, LoginPage,NotePage, ParametrePage, ArrivagePage, StockPage, SessionPage, MonitorPage,UserPage, ClientPage, PromotionPage, AboutPage, SetupPage, VentePage, NoticePage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Afficher la première frame
        if not setting.is_installed():
            self.show_frame('SetupPage')
        elif not temp_setting.get('is_login') == 'yes':
            self.show_frame('LoginPage')
        else:
            self.islogin()
            self.show_frame("MainPage")
    
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        
        if hasattr(frame,'actualise'):
            frame.actualise()
            
        frame.tkraise()
        
    def menuBar(self):
        menu = Menu(self,name='menuBar') # ma barred de menu

        #       menu option
        menu_option = Menu(menu,tearoff=0)
        menu_option.add_command(label="Accueil",command=lambda : self.show_frame('MainPage')) 
        menu_option.add_command(label="Exporter ",command=Exporte)
        menu_option.add_command(label="Parametre",command=lambda : self.show_frame('ParametrePage')) 
        menu_option.add_command(label="A propos",command=lambda : self.show_frame('AboutPage'))
        menu_option.add_command(label="Quitter",command=self.destroy)
        menu.add_cascade(menu=menu_option,label="Options")
        
        #       menu gestion
        menu_gestion = Menu(menu,tearoff=0)
        menu_gestion.add_command(label="Vente",command=lambda : self.show_frame('VentePage')) 
        menu_gestion.add_command(label="Arrivage",command=lambda : self.show_frame('ArrivagePage'))
        menu_gestion.add_command(label="Stock",command=lambda : self.show_frame('StockPage'))
        menu_gestion.add_command(label="Clients",command=lambda : self.show_frame('ClientPage'))
        menu.add_cascade(menu=menu_gestion,label="Gestion")

        #       menu  administrationmenu_outils
        menu_admin = Menu(menu,tearoff=0)
        menu_admin.add_command(label="Utilisateurs ",command=lambda : self.show_frame('UserPage'))
        menu_admin.add_command(label="Promotion ",command=lambda : self.show_frame('PromotionPage'))
        menu_admin.add_command(label="Sessions ",command=lambda : self.show_frame('SessionPage'))
        menu_admin.add_command(label="Monitoring",command=lambda : self.show_frame('MonitorPage'))
        menu.add_cascade(menu=menu_admin,label="Administration") 

        #       menu  outils
        menu_outils = Menu(menu,tearoff=0)
        menu_outils.add_command(label="Graphique",command=Graphique)
        menu_outils.add_command(label="Inventaire",command=Inventaire) 
        menu_outils.add_command(label="Notes",command=lambda : self.show_frame('NotePage'))
        menu_outils.add_command(label="Notification",command=lambda : self.show_frame('NoticePage'))
        menu.add_cascade(menu=menu_outils,label="Outils")
        
        return menu
        
    def islogin(self):
        self.config(menu=self.menuBar(),background='skyblue')
        
def run(arg=None):
    app = App()
    app.mainloop()

if __name__ == '__main__':
    run()
    
