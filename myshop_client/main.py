import tkinter as tk
from .fenetres import *

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Conteneur principal
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionnaire pour stocker les frames
        self.frames = {}
        
        # Création des différentes frames
        for F in (StartPage, PageOne, PageTwo):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Afficher la première frame
        self.show_frame("StartPage")
    
    def show_frame(self, cont):
        """Affiche la frame demandée"""
        frame = self.frames[cont]
        frame.tkraise()

def run(arg=None):
    if not setting.is_installed():
        setup()
    else:
        login_wn()
        
    if not temp_setting.get('is_login') == 'yes':
        exit(302)
    else:
        root = tk.Tk()
        root.title(temp_setting.get('boutique'))
        root.config(background='skyblue')
        #logo = pkg_resources.resource_filename('myshop','logo.ico')
        
        #root.iconbitmap(logo)
        mainframe(root)

if __name__ == '__main__':
    run()

