"""
Common declarations and functions
"""
import csv
import datetime
import logging
import operator
import os

HTTPS_ENABLED = True
HTTP_PORT = 8080
HTTPS_PORT = 8443

PWD = os.getcwd()
ROOMS_CSV = os.path.join(PWD, 'rooms.csv')
AVAILIBILITY_TEMPLATE = os.path.join(PWD, 'getavailibility_template.xml')
SERVICE_DIR = os.path.join(PWD, 'service')
CERT_DIR = os.path.join(PWD, 'certdir')
TEMPLATE_FOLDER = os.path.join(SERVICE_DIR, 'templates')

ROOMS_CACHE = None
ROOMNAMES_CACHE = None
BUILDINGS_CACHE = None
FLOORS_CACHE = {}

TIME_NOW = datetime.datetime.now().replace(microsecond=0).isoformat()
SJ_TIME_ZONE = "420"

logging.basicConfig(filename='access.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: (%(name)s) %(message)s',
                    datefmt='%a %b %d %Y %H:%M:%S')
LOGGER = logging.getLogger('roomfinder')
logging.getLogger('werkzeug').setLevel(logging.ERROR)


def end_time(start_time, duration):
    """ Calculate end time, given start time and duration """
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

def read_room_list(filename=ROOMS_CSV):
    global ROOMS_CACHE

    if ROOMS_CACHE is not None:
        return ROOMS_CACHE
    rooms = {}

    try:
        with open(filename, 'r') as fhandle:
            reader = csv.reader(fhandle)
            for room_name, room_email, room_size in reader:
                rooms[room_email] = room_name, int(room_size)
    except IOError as exception:
        LOGGER.warning("Error opening %s: %s", filename, str(exception))

    ROOMS_CACHE = rooms
    return rooms

def get_roomname_list(filename=ROOMS_CSV):
    global ROOMNAMES_CACHE

    if ROOMNAMES_CACHE is not None:
        return ROOMNAMES_CACHE

    rooms = read_room_list(filename=filename)
    roomnames = []

    for roominfo in rooms.values():
        roomnames.append(roominfo[0])

    ROOMNAMES_CACHE = sorted(roomnames)
    return ROOMNAMES_CACHE

def get_building_list(filename=ROOMS_CSV):
    global BUILDINGS_CACHE

    if BUILDINGS_CACHE is not None:
        return BUILDINGS_CACHE

    roomnames = get_roomname_list(filename=filename)
    buildings = set()
    for roomname in roomnames:
        buildings.add(roomname.split('-')[0])

    BUILDINGS_CACHE = sorted(buildings)
    return BUILDINGS_CACHE

def get_floor_list(buildingname, filename=ROOMS_CSV):
    if buildingname in FLOORS_CACHE:
        return FLOORS_CACHE[buildingname]

    roomnames = get_roomname_list(filename=filename)
    floors = set()
    for roomname in roomnames:
        if roomname.startswith(buildingname):
            floors.add(roomname.split('-')[1])

    FLOORS_CACHE[buildingname] = sorted(floors)
    return FLOORS_CACHE[buildingname]

def write_room_list(rooms, filename=ROOMS_CSV):
    global ROOMS_CACHE
    ROOMS_CACHE = rooms

    with open(filename, "wb") as fhandle:
        writer = csv.writer(fhandle)
        for email, room_info in sorted(rooms.iteritems(), key=operator.itemgetter(1)):
            name, size = room_info
            writer.writerow([name, email, size])
