#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import getpass
import subprocess
import sys
import xml.etree.ElementTree as ET

from string import Template

URL = 'https://mail.cisco.com/ews/exchange.asmx'
SCHEME_TYPES = './/{http://schemas.microsoft.com/exchange/services/2006/types}'
TIME_NOW = datetime.datetime.now().replace(microsecond=0).isoformat()
TIME_1H_FROM_NOW = None

reload(sys)
sys.setdefaultencoding("utf-8")

def read_room_list(filename='rooms.csv'):
    rooms = {}

    with open(filename, 'r') as fhandle:
        reader = csv.reader(fhandle)
        for row in reader:
            rooms[unicode(row[1])] = unicode(row[0])

    return rooms


def find_available_rooms(rooms, user, password, start_time=TIME_NOW, end_time=None):
    if end_time is None:
        start = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        end_time = (start + datetime.timedelta(hours=1)).isoformat()

    print "Searching for a room from " + start_time + " to " + end_time + ":"
    print "{0:10s} {1:64s} {2:64s}".format("Status", "Room", "Email")

    xml_template = open("getavailibility_template.xml", "r").read()
    xml = Template(xml_template)
    for room in rooms:
        data = unicode(xml.substitute(email=room, starttime=start_time, endtime=end_time))

        header = "\"content-type: text/xml;charset=utf-8\""
        command = "curl --silent --header " + header \
                   + " --data '" + data \
                   + "' --ntlm " \
                   + "-u "+ user + ":" + password \
                   + " " + URL
        response = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]

        tree = ET.fromstring(response)

        status = "Free"
        # arrgh, namespaces!!
        elems = tree.findall(SCHEME_TYPES + "BusyType")
        for elem in elems:
            status = elem.text

        print "{0:10s} {1:64s} {2:64s}".format(status, rooms[room], room)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="user name for exchange/outlook", required=True)
    parser.add_argument("-start", "--starttime",
                        help="Starttime e.g. 2014-07-02T11:00:00 (default = now)",
                        default=TIME_NOW)
    parser.add_argument("-end", "--endtime",
                        help="Endtime e.g. 2014-07-02T12:00:00 (default = now+1h)",
                        default=TIME_1H_FROM_NOW)
    parser.add_argument("-f", "--file",
                        help="csv filename with room info (default=rooms.csv).",
                        default="rooms.csv")

    args = parser.parse_args()
    args.password = getpass.getpass("Password:")

    rooms = read_room_list()
    find_available_rooms(rooms, args.user, args.password, args.starttime, args.endtime)


if __name__ == '__main__':
    run()
