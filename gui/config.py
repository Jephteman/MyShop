import os
import client
import pathlib
from configparser import ConfigParser


conf_file = pathlib.Path(os.getcwd()).joinpath('.config.txt')

config = ConfigParser()
config.read(conf_file.__str__())

is_installed = conf_file.is_file() # check if config file exist

client._cred['url'] = config.get('DEFAULT','url') if config.has_option('DEFAULT','url') else ''
shop_name = config.get('DEFAULT','name') if config.has_option('DEFAULT','name') else ''

uname = ''

client_id = {'id':1}
