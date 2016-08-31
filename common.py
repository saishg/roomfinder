import datetime
import logging
import os

URL = 'https://mail.cisco.com/ews/exchange.asmx'
SCHEME_TYPES = './/{http://schemas.microsoft.com/exchange/services/2006/types}'
HTTPS_ENABLED = True
HTTP_PORT = 8080
HTTPS_PORT = 8443

PWD = os.getcwd()
ROOMS_CSV = os.path.join(PWD, 'rooms.csv')
ROOMS_SEARCH_CSV = os.path.join(PWD, 'roomssearch.csv')
AVAILIBILITY_TEMPLATE = os.path.join(PWD, 'getavailibility_template.xml')
SERVICE_DIR = os.path.join(PWD, 'service')
CERT_DIR = os.path.join(PWD, 'certdir')
TEMPLATE_FOLDER = os.path.join(SERVICE_DIR, 'templates')

TIME_NOW = datetime.datetime.now().replace(microsecond=0).isoformat()
TIME_1H_FROM_NOW = None
SJ_TIME_ZONE = "420"

logging.basicConfig(filename='access.log',level=logging.DEBUG)
LOGGER = logging.getLogger('roomfinder')
logging.getLogger('werkzeug').setLevel(logging.ERROR)
