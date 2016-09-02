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

logging.basicConfig(filename='access.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: (%(name)s) %(message)s',
                    datefmt='%a %b %d %Y %H:%M:%S')
LOGGER = logging.getLogger('roomfinder')
logging.getLogger('werkzeug').setLevel(logging.ERROR)


def end_time(start_time, duration):
    try:
        if 'h' in duration and duration.endswith('m'):
            hours, mins = map(int, duration[:-1].split('h'))
        elif duration.endswith('h'):
            hours, mins = int(duration[:-1]), 0
        elif duration.endswith('m'):
            hours, mins = 0, int(duration[:-1])
        else:
            duration = int(duration)
            if duration < 15:
                hours, mins = duration, 0
            else:
                hours, mins = 0, duration
    except ValueError:
        hours, mins = 1, 0

    start = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    return (start + datetime.timedelta(hours=hours, minutes=mins)).isoformat()
