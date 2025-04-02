import os    
import platform
import pathlib
from waitress import serve
from .app import app as app, prepare
from .install import run as install
from configparser import ConfigParser


def run(arg=None):
     # Détecter le système d'exploitation
    if platform.system() == "Windows":
        config_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "myshop")
    else:
        config_dir = os.path.expanduser("~/.config/myshop")

    config_file = os.path.join(config_dir, "config.txt")

    if not pathlib.Path(config_file).exists():
        install()
    else:
        config = ConfigParser()
        config.read(config_file)
        is_installed = config.has_option('SERVEUR','IS_INSTALLED')
        if not is_installed:
            install()

    os.chdir(config_dir)

    print('[+] Lancement du serveur ')
    prepare()
    serve(
        app,
        host=config.get('SERVEUR','network'),
        port=config.get('SERVEUR','port')
        )
if __name__ == '__main__':
    run()