import tkinter as tk
from .fenetres import *


def run(arg=None):
    if not setting.is_installed():
        setup()
    else:
        login_wn()
        
    if not client._cred.get('cookie',None):
        exit(302)
    else:
        root = tk.Tk()
        root.title(client._cred.get('boutique'))
        root.config(background='skyblue')
        logo = pkg_resources.resource_filename('myshop','logo.ico')
        
        root.iconbitmap(logo)
        mainframe(root)

if __name__ == '__main__':
    run()

