"""
Webservice APIs for room finder backend
"""

import collections
import json
import os
import socket

import common
import flask

from book_room import ReserveAvailRoom
from find_available_room import AvailRoomFinder

APP = flask.Flask(__name__, template_folder=common.TEMPLATE_FOLDER)

@APP.route('/')
def index():
    """ Serve static index file """
    return flask.render_template('index3.html')

QueryParam = collections.namedtuple('QueryParam', 'buildingname, floor, date, starttime, endtime, user, password, attendees, timezone')
BookRoomQueryParam = collections.namedtuple('QueryParam', 'roomname, date, starttime, endtime, user, password, timezone')

@APP.route('/getcity', methods=['GET'])
def get_city():
    """ Get closest city in JSON """
    latitude = flask.request.args.get('latitude')
    longitude = flask.request.args.get('longitude')
    city = common.get_closest_city(float(latitude), float(longitude))
    common.LOGGER.info("Closest city is %s based on coordinates: %s, %s",
                       city, latitude, longitude)
    return json.dumps(city)

@APP.route('/showcities', methods=['GET'])
def show_cities():
    """ Serve list of cities in JSON """
    cities = common.get_city_list()
    common.LOGGER.debug("Read list of %d cities from database", len(cities))
    return json.dumps(cities)

@APP.route('/showbuildings', methods=['GET'])
def show_buldings():
    """ Serve list of buildings in JSON """
    city = flask.request.args.get('city')
    buildings = common.get_building_list(city)
    common.LOGGER.debug("%d buildings in %s", len(buildings), city)
    return json.dumps(buildings)

@APP.route('/showfloors', methods=['GET'])
def show_floors():
    """ Serve list of floors in JSON """
    buildingname = flask.request.args.get('buildingname')
    floors = common.get_floor_list(buildingname)
    common.LOGGER.debug("%d floors in %s", len(floors), buildingname)
    if len(floors) > 1:
        return json.dumps(floors + ["Any"])
    else:
        return json.dumps(floors)

# Example Query
# http://127.0.0.1:5000/showrooms?building_floor_name=ABC&starttime=2016-08-25T09:00:00-13:00&duration=1h&user=USER&password=password
@APP.route('/showrooms', methods=['GET'])
def show_rooms():
    """ Serve list of rooms in JSON """
    queryparam = QueryParam(buildingname=flask.request.args.get('buildingname'),
                            floor=flask.request.args.get('floor'),
                            date=flask.request.args.get('date'),
                            starttime=flask.request.args.get('starttime'),
                            endtime=flask.request.args.get('endtime'),
                            user=flask.request.args.get('user'),
                            password=flask.request.args.get('password'),
                            attendees=flask.request.args.get('attendees'),
                            timezone=flask.request.args.get('timezone'))

    if queryparam.floor.startswith("Any"):
        prefix = queryparam.buildingname
    else:
        prefix = queryparam.buildingname + '-' + queryparam.floor

    try:
        room_finder = AvailRoomFinder(user=queryparam.user,
                                      password=queryparam.password,
                                      start_time=queryparam.date + "T" + queryparam.starttime + ":00",
                                      end_time=queryparam.date + "T" + queryparam.endtime + ":00",
                                      timezone=queryparam.timezone)
        rooms_info = room_finder.search_free(prefix, min_size=int(queryparam.attendees))
    except Exception as exception:
        common.LOGGER.warning("User %s query resulted in an error: %s",
                              queryparam.user, str(exception))
        rooms_info = {"Error" : str(exception)}
    return json.dumps(rooms_info)

@APP.route('/bookroom', methods=['GET'])
def book_room():
    """ Reserve specified room """
    queryparam = BookRoomQueryParam(roomname=flask.request.args.get('roomname'),
                                    date=flask.request.args.get('date'),
                                    starttime=flask.request.args.get('starttime'),
                                    endtime=flask.request.args.get('endtime'),
                                    user=flask.request.args.get('user'),
                                    password=flask.request.args.get('password'),
                                    timezone=flask.request.args.get('timezone'))

    room_finder = ReserveAvailRoom(user=queryparam.user,
                                   password=queryparam.password,
                                   roomname=queryparam.roomname,
                                   start_time=queryparam.date + "T" + queryparam.starttime + ":00",
                                   end_time=queryparam.date + "T" + queryparam.endtime + ":00",
                                   timezone=queryparam.timezone)
    try:
        if room_finder.reserve_room():
            common.LOGGER.warning("User %s reservation of %s succeeded",
                                  queryparam.user, queryparam.roomname)
            return "reservation requested"
        else:
            common.LOGGER.warning("User %s reservation of %s failed",
                                  queryparam.user, queryparam.roomname)
            return "reservation failed"
    except Exception as exception:
        common.LOGGER.warning("User %s reservation of %s resulted in an error: %s",
                              queryparam.user, queryparam.roomname, str(exception))
        return "reservation failed: " + str(exception)

def create_ssl_context():
    """ Create SSL context """
    context = (os.path.join(common.CERT_DIR, 'roomfinder.cert'),
               os.path.join(common.CERT_DIR, 'roomfinder.key'))
    return context

if __name__ == '__main__':
    if common.HTTPS_ENABLED:
        APP.run(threaded=True, host=socket.gethostname(),
                ssl_context=create_ssl_context(), port=common.HTTPS_PORT)
    else:
        APP.run(threaded=True, host=socket.gethostname(),
                port=common.HTTP_PORT)