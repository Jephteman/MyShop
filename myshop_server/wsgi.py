from waitress import serve
from .app import app as app, prepare
from configparser import ConfigParser

def run(arg=None):
    config = ConfigParser()
    config.read('.env')
   
    print('[+] Lancement du serveur ')
    
    prepare(config._sections['GENERAL_SETTING'])
    serve(
        app,
        host=config.get('GENERAL_SETTING','network'),
        port=config.get('GENERAL_SETTING','port')
        )
    
if __name__ == '__main__':
    run()
