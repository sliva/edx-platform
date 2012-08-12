"""
This config file runs the simplest dev environment using sqlite, and db-based
sessions. Assumes structure:

/envroot/
        /db   # This is where it'll write the database file
        /mitx # The location of this repo
        /log  # Where we're going to write log files
"""
from .common import *
from .logsettings import get_logger_config
from .dev import *
import socket

WIKI_ENABLED = False
MITX_FEATURES['ENABLE_TEXTBOOK'] = False
MITX_FEATURES['ENABLE_DISCUSSION'] = False
MITX_FEATURES['ACCESS_REQUIRE_STAFF_FOR_COURSE'] = True	  # require that user be in the staff_* group to be able to enroll

myhost = socket.gethostname()
if ('edxvm' in myhost) or ('ocw' in myhost):
    MITX_FEATURES['DISABLE_LOGIN_BUTTON'] = True	# auto-login with MIT certificate
    MITX_FEATURES['USE_XQA_SERVER'] = 'https://qisx.mit.edu/xqa'	# needs to be ssl or browser blocks it

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')	# django 1.4 for nginx ssl proxy

#-----------------------------------------------------------------------------
# disable django debug toolbars

INSTALLED_APPS = tuple([ app for app in INSTALLED_APPS if not app.startswith('debug_toolbar') ])
MIDDLEWARE_CLASSES = tuple([ mcl for mcl in MIDDLEWARE_CLASSES if not mcl.startswith('debug_toolbar') ])
TEMPLATE_LOADERS = tuple([ app for app in TEMPLATE_LOADERS if not app.startswith('askbot') ])
