"""
Webservice APIs for room finder backend
"""

import collections
import json
import os
import shutil
import socket


import common
import flask

from book_room import ReserveAvailRoom
from find_available_room import AvailRoomFinder

APP = flask.Flask(__name__, template_folder=common.TEMPLATE_FOLDER)

@APP.route('/')
def index():
    """ Serve static index file """
    return flask.render_template('index.html')

QueryParam = collections.namedtuple('QueryParam', 'buildingname, floor, starttime, duration, user, password, attendees, timezone')
BookRoomQueryParam = collections.namedtuple('QueryParam', 'roomname, roomemail, starttime, duration, user, password, timezone')

@APP.route('/showbuldings', methods=['GET'])
def show_buldings():
    """ Serve list of buildings in JSON """
    buldings = []
    with open(common.ROOMS_CSV, 'r') as fhandle:
        for line in fhandle.readlines():
            buldingname = line.split('-')[0]
            if buldingname not in buldings:
                buldings.append(buldingname)
    return json.dumps(buldings)


# Example Query
# http://127.0.0.1:5000/showrooms?building_floor_name=ABC&starttime=2016-08-25T09:00:00-13:00&duration=1h&user=USER&password=password
@APP.route('/showrooms', methods=['GET'])
def show_rooms():
    """ Serve list of buildings in JSON """
    queryparam = QueryParam(buildingname=flask.request.args.get('buildingname'),
                            floor=flask.request.args.get('floor'),
                            starttime=flask.request.args.get('starttime'),
                            duration=flask.request.args.get('duration'),
                            user=flask.request.args.get('user'),
                            password=flask.request.args.get('password'),
                            attendees=flask.request.args.get('attendees'),
                            timezone=flask.request.args.get('timezone'))

    prefix = queryparam.buildingname + '-' + queryparam.floor
    _create_tmp_rooms_file(prefix)

    try:
        room_finder = AvailRoomFinder(user=queryparam.user,
                                      password=queryparam.password,
                                      start_time=queryparam.starttime,
                                      duration=queryparam.duration,
                                      filename=common.ROOMS_SEARCH_CSV,
                                      timezone=queryparam.timezone)
        rooms_info = room_finder.search_free(prefix, min_size=int(queryparam.attendees))
    except Exception as exception:
        rooms_info = {"Error" : str(exception)}
    return json.dumps(rooms_info)

@APP.route('/bookroom', methods=['GET'])
def book_room():
    """ Reserve specified room """
    queryparam = BookRoomQueryParam(roomname=flask.request.args.get('roomname'),
                                    roomemail=flask.request.args.get('roomemail'),
                                    starttime=flask.request.args.get('starttime'),
                                    duration=flask.request.args.get('duration'),
                                    user=flask.request.args.get('user'),
                                    password=flask.request.args.get('password'),
                                    timezone=flask.request.args.get('timezone'))
    room_finder = ReserveAvailRoom(user=queryparam.user,
                                   password=queryparam.password,
                                   roomname=queryparam.roomname,
                                   roomemail=queryparam.roomemail,
                                   start_time=queryparam.starttime,
                                   duration=queryparam.duration,
                                   timezone=queryparam.timezone)
    try:
        if room_finder.reserve_room():
            return "reservation requested"
        else:
            return "reservation failed"
    except Exception as excpetion:
        return "reservation failed: " + str(excpetion)

def _create_tmp_rooms_file(building_floor_name):
    if 'all' in building_floor_name:
        shutil.copyfile(common.ROOMS_CSV, common.ROOMS_SEARCH_CSV)
    else:
        open(common.ROOMS_SEARCH_CSV, 'w').writelines([line for line in open(common.ROOMS_CSV) if building_floor_name in line])

def create_ssl_context():
    """ Create SSL context """
    context = (os.path.join(common.CERT_DIR, 'roomfinder.cert'), os.path.join(common.CERT_DIR, 'roomfinder.key'))
    return context

if __name__ == '__main__':
    if common.HTTPS_ENABLED:
        APP.run(threaded=True, host=socket.gethostname(), ssl_context=create_ssl_context(), port=common.HTTPS_PORT)
    else:
        APP.run(threaded=True, host=socket.gethostname(), port=common.HTTP_PORT)
