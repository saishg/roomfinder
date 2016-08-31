import common
import flask
import json
import os
import socket

from book_room import ReserveAvailRoom
from collections import namedtuple
from find_available_room import AvailRoomFinder
from shutil import copyfile
from flask import Flask, request

app = Flask(__name__, template_folder=common.TEMPLATE_FOLDER)

@app.route('/')
def index():
    return flask.render_template('index.html')

QueryParam = namedtuple('QueryParam', 'buildingname, floor, starttime, duration, user, password, attendees, timezone' )
BookRoomQueryParam  = namedtuple('QueryParam', 'roomname, roomemail, starttime, duration, user, password, timezone')

@app.route('/showbuldings', methods=['GET'])
def show_buldings():
    buldings = []
    with open(common.ROOMS_CSV, 'r') as f:
        for line in f.readlines():
            buldingname = line.split('-')[0]
            if buldingname not in buldings:
                buldings.append(buldingname)
    return json.dumps(buldings)


# Example Query
# http://127.0.0.1:5000/showrooms?building_floor_name=ABC&starttime=2016-08-25T09:00:00-13:00&duration=1h&user=USER&password=password
@app.route('/showrooms', methods=['GET'])
def show_rooms():
    queryparam = QueryParam(
                            buildingname=request.args.get('buildingname'),
                            floor=request.args.get('floor'),
                            starttime=request.args.get('starttime'),
                            duration=request.args.get('duration'),
                            user = request.args.get('user'),
                            password = request.args.get('password'),
                            attendees = request.args.get('attendees'),
                            timezone = request.args.get('timezone'),
                            )

    prefix = queryparam.buildingname + '-' + queryparam.floor
    _create_tmp_rooms_file(prefix)

    try:
        room_finder = AvailRoomFinder(queryparam.user, queryparam.password,
                                      queryparam.starttime,
                                      duration=queryparam.duration,
                                      roominfo=common.ROOMS_SEARCH_CSV,
                                      timezone=queryparam.timezone)
        rooms_info = room_finder.search_free(prefix, min_size=int(queryparam.attendees))
    except Exception as e:
        rooms_info = {"Error: " + str(e) : ""}
    return json.dumps(rooms_info)

@app.route('/bookroom', methods=['GET'])
def book_room():
    queryparam = BookRoomQueryParam(
                            roomname=request.args.get('roomname'),
                            roomemail=request.args.get('roomemail'),
                            starttime=request.args.get('starttime'),
                            duration=request.args.get('duration'),
                            user = request.args.get('user'),
                            password = request.args.get('password'),
                            timezone = request.args.get('timezone'),
                            )
    room_finder = ReserveAvailRoom(queryparam.roomname,
                                   queryparam.roomemail,
                                   queryparam.user,
                                   queryparam.password,
                                   queryparam.starttime,
                                   duration=queryparam.duration,
                                   timezone=queryparam.timezone)
    rooms_info = room_finder.reserve_room()

    if 'Success' in rooms_info:
        return "reservation requested"

    return "reservation failed"

def _create_tmp_rooms_file(building_floor_name):
    if 'all' in building_floor_name:
        copyfile(common.ROOMS_CSV, common.ROOMS_SEARCH_CSV)
    else:
        open(common.ROOMS_SEARCH_CSV, 'w').writelines([ line for line in open(common.ROOMS_CSV) if building_floor_name in line])

def create_context():
    context = (os.path.join(common.CERT_DIR, 'roomfinder.cert'), os.path.join(common.CERT_DIR, 'roomfinder.key'))
    return context

if __name__ == '__main__':
    if common.HTTPS_ENABLED:
        app.run(debug=True, threaded=True, host=socket.gethostname(), ssl_context=create_context(), port=common.HTTPS_PORT)
    else:
        app.run(debug=True, threaded=True, host=socket.gethostname(), port=common.HTTP_PORT)
