"""
Common declarations and functions
"""
import csv
import datetime
import logging
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
CITIES_CACHE = None
BUILDINGS_CACHE = {}
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
            for room_name, room_email, room_size, city, country in reader:
                rooms[room_name] = {"name" : room_name,
                                    "size" : int(room_size),
                                    "email" : room_email,
                                    "city" : city,
                                    "country" : country,
                                   }
    except IOError as exception:
        LOGGER.warning("Error opening %s: %s", filename, str(exception))

    ROOMS_CACHE = rooms
    return rooms

def get_roomname_list(filename=ROOMS_CSV):
    global ROOMNAMES_CACHE

    if ROOMNAMES_CACHE is not None:
        return ROOMNAMES_CACHE

    rooms = read_room_list(filename=filename)
    ROOMNAMES_CACHE = sorted(rooms)
    return ROOMNAMES_CACHE

def get_building_list(city, filename=ROOMS_CSV):
    if city in BUILDINGS_CACHE:
        return BUILDINGS_CACHE[city]

    rooms = read_room_list(filename=filename)
    buildings = set()
    for roomname, roominfo in rooms.iteritems():
        if roominfo["city"] == city:
            buildings.add(roomname.split('-')[0])

    BUILDINGS_CACHE[city] = sorted(buildings)
    return BUILDINGS_CACHE[city]

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

def get_city_list(filename=ROOMS_CSV):
    global CITIES_CACHE

    if CITIES_CACHE is not None:
        return CITIES_CACHE

    rooms = read_room_list(filename=filename)
    cities = set()
    for roominfo in rooms.itervalues():
        cities.add(roominfo["city"])

    CITIES_CACHE = sorted(cities)
    return CITIES_CACHE

def write_room_list(rooms, filename=ROOMS_CSV):
    global ROOMS_CACHE
    ROOMS_CACHE = rooms

    with open(filename, "wb") as fhandle:
        writer = csv.writer(fhandle)
        for name in sorted(rooms):
            room_info = rooms[name]
            email = room_info["email"]
            size = room_info["size"]
            city = room_info["city"]
            country = room_info["country"]
            writer.writerow([name, email, size, city, country])
