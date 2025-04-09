import tkinter as tk
from .fenetres import *


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
        logo = pkg_resources.resource_filename('myshop','logo.ico')
        
        root.iconbitmap(logo)
        mainframe(root)

if __name__ == '__main__':
    run()

