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
    
    rooms = {}
    for row in csv.reader(open(CONFIG['roomssearchcsv'], 'r')):
        rooms[row[1]]=(row[0])

    xml_template = open(CONFIG['availibility_template'], "r").read()
    xml = Template(xml_template)
    resp = []
    
    for room in rooms:
        data = unicode(xml.substitute(email=room,
                                      starttime=queryparam.starttime,
                                      endtime=queryparam.endtime))
        header = "\"content-type: text/xml;charset=utf-8\""
        command = "curl --silent --header " + header +" --data '" + data + "' --ntlm "\
                + "-u "+ queryparam.user+":"+queryparam.password+" "+ CONFIG['URL']
        response = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
        tree = ET.fromstring(response)
        status = "Free"
        elems = tree.findall(".//{http://schemas.microsoft.com/exchange/services/2006/types}BusyType")
        for elem in elems:
            status = elem.text
        subject = ""
        elems = tree.findall(".//{http://schemas.microsoft.com/exchange/services/2006/types}Subject")
        for elem in elems:
            subject += elem.text
        
        resp.append({'status':status, 'room' : rooms[room], 'roomid' : room, 'subject' : subject})         
        
    return json.dumps(resp)

def _create_tmp_rooms_file(roomname):
    if 'all' in roomname:
        copyfile(CONFIG['roomscsv'], CONFIG['roomssearchcsv'])
    else:
        open(CONFIG['roomssearchcsv'],'w').writelines([ line for line in open(CONFIG['roomscsv']) if roomname in line])

if __name__ == '__main__':
    app.run(debug=True)
