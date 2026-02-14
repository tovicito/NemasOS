import os

APP_ID = 'tte.nemas.Epola'
VERSION = '0.1.0'

# In a real installed app, these would be set by Meson
PKGDATADIR = os.environ.get('PKGDATADIR', os.path.dirname(os.path.dirname(__file__)))
