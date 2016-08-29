from collections import namedtuple
from find_available_room import AvailRoomFinder
from book_room import ReserveAvailRoom
import flask
import json
import os
import socket

from shutil import copyfile
from flask import Flask, request

PWD = os.getcwd()

CONFIG = {
        'home' : PWD,
        'roomscsv' : os.path.join(PWD, 'rooms.csv'),
        'roomssearchcsv' : os.path.join(PWD, 'roomssearch.csv'),
        'availibility_template' : os.path.join(PWD, 'getavailibility_template.xml'),
        'URL': "https://mail.cisco.com/ews/exchange.asmx",
        'allrooms' :  os.path.join(PWD, 'allrooms.csv'),
        'certdir' : os.path.join(PWD, 'certdir')
        }

app = Flask(__name__, template_folder=CONFIG['home'] + '/service/templates')

@app.route('/')
def index():
    return flask.render_template('index.html')

QueryParam = namedtuple('QueryParam', 'buildingname, floor, starttime, duration, user, password, attendees, timezone' )
BookRoomQueryParam  = namedtuple('QueryParam', 'roomname, roomemail, starttime, duration, user, password, timezone')

@app.route('/showbuldings', methods=['GET'])
def show_buldings():
    buldings = []
    with open(CONFIG['allrooms'],'r') as f:
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
                                      roominfo=CONFIG['roomssearchcsv'],
                                      timezone=queryparam.timezone)
        rooms_info = room_finder.search_free(prefix, min_size=int(queryparam.attendees),
                                             print_to_stdout=True)
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
    rooms_info = room_finder.reserve_room(print_to_stdout=True)

    if 'Success' in rooms_info:
        return "reservation requested"

    return "reservation failed"

def _create_tmp_rooms_file(building_floor_name):
    if 'all' in building_floor_name:
        copyfile(CONFIG['roomscsv'], CONFIG['roomssearchcsv'])
    else:
        open(CONFIG['roomssearchcsv'],'w').writelines([ line for line in open(CONFIG['roomscsv']) if building_floor_name in line])

def create_context():
    context = (os.path.join(CONFIG['certdir'], 'roomfinder.cert'), os.path.join(CONFIG['certdir'], 'roomfinder.key'))
    return context

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host=socket.gethostname(), ssl_context=create_context(), port=5001)
