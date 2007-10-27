"""reads config for restserver and converter from docutils.conf
$Id: config.py 24 2007-09-04 13:29:30Z christofh $ 
"""
from ConfigParser import ConfigParser

__config = ConfigParser()
__config.read('docutils.conf')

PATH = __config.get('server', 'path')
PORT = __config.getint('server', 'port')
RST_EXT = __config.get('server', 'extension')
RST_ROOT = __config.get('server', 'root')

TARGETDIR = __config.get('converter', 'targetdir')

