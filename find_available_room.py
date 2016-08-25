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
TIME_ZONE = '-13:00' #PST HACK

reload(sys)
sys.setdefaultencoding("utf-8")

class AvailRoomFinder(object):

    def __init__(self, user, password,
                 start_time=TIME_NOW, end_time=None,
                 roominfo='rooms.csv'):
        self.rooms = self._read_room_list(roominfo)
        self.user = user
        self.password = password
        self.start_time = start_time
        if end_time is None:
            start = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
            self.end_time = (start + datetime.timedelta(hours=1)).isoformat()
        else:
            self.end_time = end_time

    def _read_room_list(self, filename):
        rooms = {}

        with open(filename, 'r') as fhandle:
            reader = csv.reader(fhandle)
            for row in reader:
                rooms[unicode(row[1])] = (unicode(row[0]), int(row[2]))

        return rooms

    def search_free(self, prefix, min_size=1, print_to_stdout=False):
        selected_rooms = {}
        for email in self.rooms:
            name, size = self.rooms[email]
            if name.startswith(prefix) and size > min_size:
                selected_rooms[email] = (name, size)

        selected_room_info = self.search(selected_rooms, print_to_stdout)
        free_room_info = {}
        for email in selected_room_info:
            if selected_room_info[email]['status'] == 'Free':
                free_room_info[email] = selected_room_info[email]
        return free_room_info

    def search(self, selected_rooms=None, print_to_stdout=False):
        if selected_rooms is None:
            selected_rooms = self.rooms()
        room_info = {}

        if print_to_stdout:
            print "Searching for a room from " + self.start_time + " to " + self.end_time + ":"
            print "{0:20s} {1:64s} {2:64s}".format("Status", "Room", "Email")

        xml_template = open("getavailibility_template.xml", "r").read()
        xml = Template(xml_template)

        for email in selected_rooms:
            data = unicode(xml.substitute(email=email,
                                          starttime=self.start_time + TIME_ZONE,
                                          endtime=self.end_time + TIME_ZONE))

            header = "\"content-type: text/xml;charset=utf-8\""
            command = "curl --silent --header " + header \
                       + " --data '" + data \
                       + "' --ntlm " \
                       + "-u "+ self.user + ":" + self.password \
                       + " " + URL
            response = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
            if not response:
                return room_info

            tree = ET.fromstring(response)

            status = "Free"
            elems = tree.findall(SCHEME_TYPES + "MergedFreeBusy")
            for elem in elems:
                freebusy = elem.text
                if '2' in freebusy:
                    status = "Busy"
                elif '3' in freebusy:
                    status = "Unavailable"
                elif '1' in freebusy:
                    status = "Tentative"

            name, size = self.rooms[email]
            room_info[name] = {'size': size, 'freebusy': freebusy, 'status': status}

            if print_to_stdout:
                print "{0:20s} {1:64s} {2:64s}".format(status + '-' + freebusy, self.rooms[email], email)

        return room_info

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="user name for exchange/outlook", required=True)
    parser.add_argument("-prefix", "--prefix",
                        help="A prefix to search for. e.g. 'SJC19- SJC18-'",
                        default='')
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

    room_finder = AvailRoomFinder(args.user, args.password, args.starttime, args.endtime, args.file)
    print room_finder.search_free(prefix=args.prefix, print_to_stdout=True)


if __name__ == '__main__':
    run()
