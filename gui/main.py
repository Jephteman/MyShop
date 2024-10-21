from tkinter import *
from fenetres import *


if __name__ == '__main__':
    if not is_installed:
        setup()

    else:
        login_wn()
        
    if not client._cred.get('cookie',None):
        exit(302)

    root = Tk(className=shop_name)
    mainframe(root)

