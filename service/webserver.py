import codecs
import csv
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as ET

from collections import namedtuple
from flask import Flask
from shutil import copyfile
from string import Template
from find_available_room import AvailRoomFinder

PWD = os.getcwd()

CONFIG = { 
        'home' : PWD,
        'roomscsv' : PWD + '/rooms.csv',
        'roomssearchcsv' : PWD + '/roomssearch.csv',  
        'availibility_template' : PWD + '/getavailibility_template.xml', 
        'URL': "https://mail.cisco.com/ews/exchange.asmx"
        }

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to Room Finder Web Service"


from flask import request

QueryParam = namedtuple('QueryParam', 'roomname, starttime, endtime, user, password')

# Example Query 
# http://127.0.0.1:5000/showrooms?roomname=ABC&starttime=2016-08-25T09:00:00-13:00&endtime=2016-08-25T10:00:00-13:00&user=USER&password=password
@app.route('/showrooms', methods=['GET'])
def show_rooms():
    queryparam = QueryParam(
                            roomname=request.args.get('roomname'),
                            starttime=request.args.get('starttime'),
                            endtime=request.args.get('endtime'),
                            user = request.args.get('user'),
                            password = request.args.get('password'),
                            )

    _create_tmp_rooms_file(queryparam.roomname)
    
    room_finder = AvailRoomFinder(queryparam.user, queryparam.password, queryparam.starttime, queryparam.endtime, CONFIG['roomssearchcsv'])
    rooms_info = room_finder.search(print_to_stdout=True)

    return json.dumps(rooms_info)

def _create_tmp_rooms_file(roomname):
    if 'all' in roomname:
        copyfile(CONFIG['roomscsv'], CONFIG['roomssearchcsv'])
    else:
        open(CONFIG['roomssearchcsv'],'w').writelines([ line for line in open(CONFIG['roomscsv']) if roomname in line])

if __name__ == '__main__':
    app.run(debug=True)