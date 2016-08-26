import codecs
from collections import namedtuple
import csv
import datetime
from find_available_room import AvailRoomFinder 
from book_room import ReserveAvailRoom
from flask import Flask
import flask
import json
import os
from shutil import copyfile
from string import Template
import subprocess
import xml.etree.ElementTree as ET
from flask import Flask, request

PWD = os.getcwd()

CONFIG = { 
        'home' : PWD,
        'roomscsv' : PWD + '/rooms.csv',
        'roomssearchcsv' : PWD + '/roomssearch.csv',  
        'availibility_template' : PWD + '/getavailibility_template.xml', 
        'URL': "https://mail.cisco.com/ews/exchange.asmx",
        'allrooms' :  PWD + '/allrooms.csv',
        }

app = Flask(__name__, template_folder=CONFIG['home'] + '/service/templates')

@app.route('/')
def index():
    return flask.render_template('index.html')

QueryParam = namedtuple('QueryParam', 'buildingname, floor, starttime, duration, user, password attendees' )
BookRoomQueryParam  = namedtuple('QueryParam', 'roomid, starttime, duration, user, password')

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
                            )

    prefix = queryparam.buildingname + '-' + queryparam.floor
    _create_tmp_rooms_file(prefix)
   
    try: 
        room_finder = AvailRoomFinder(queryparam.user, queryparam.password,
                                      queryparam.starttime, queryparam.duration,
                                      CONFIG['roomssearchcsv'])
        rooms_info = room_finder.search_free(prefix, min_size=int(queryparam.attendees),
                                             print_to_stdout=True)
    except Exception as e:
        rooms_info = {"Error:" + str(e) : ""}
    return json.dumps(rooms_info)

@app.route('/bookroom', methods=['GET'])
def book_room():
    queryparam = BookRoomQueryParam(
                            roomid=request.args.get('roomid'),
                            starttime=request.args.get('starttime'),
                            duration=request.args.get('duration'),
                            user = request.args.get('user'),
                            password = request.args.get('password'),
                            )
    room_finder = ReserveAvailRoom(queryparam.roomid, queryparam.user, queryparam.password,
                                      queryparam.starttime, 
                                      CONFIG['roomssearchcsv'],
                                      queryparam.duration)
    rooms_info = room_finder.reserve_room(queryparam.roomid, print_to_stdout=True)
    
    if 'Success' in rooms_info:
        return "Room Reserved Successfully"

    return "Reserve Room failed"

def _create_tmp_rooms_file(building_floor_name):
    if 'all' in building_floor_name:
        copyfile(CONFIG['roomscsv'], CONFIG['roomssearchcsv'])
    else:
        open(CONFIG['roomssearchcsv'],'w').writelines([ line for line in open(CONFIG['roomscsv']) if building_floor_name in line])

if __name__ == '__main__':
    app.run(debug=True)
