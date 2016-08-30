#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import base64
import common
import csv
import datetime
import getpass
import subprocess
import sys
import threading
import urllib
import xml.etree.ElementTree as ET

from string import Template

reload(sys)
sys.setdefaultencoding("utf-8")

class AvailRoomFinder(object):

    def __init__(self, user, password,
                 start_time=common.TIME_NOW, duration='1h',
                 roominfo='rooms.csv', timezone=common.SJ_TIME_ZONE):
        self.rooms = self._read_room_list(roominfo)
        self.user = user
        self.password = password
        self.start_time = start_time
        self.room_info = {}
        self.timezone = timezone or common.SJ_TIME_ZONE

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
        self.end_time = (start + datetime.timedelta(hours=hours, minutes=mins)).isoformat()

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
            if name.startswith(prefix) and size >= min_size:
                selected_rooms[email] = (name, size)

        selected_room_info = self.search(selected_rooms, print_to_stdout)
        free_room_info = {}
        for email in selected_room_info:
            if selected_room_info[email]['status'] == 'Free':
                free_room_info[email] = selected_room_info[email]
        return free_room_info

    def room_name(self, email):
        return self.rooms[email][0]

    def _query(self, command, email, print_to_stdout=False):
        if print_to_stdout:
            print "Querying for {}".format(self.room_name(email))

        response = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
        if not response:
            print "No response for room {}".format(self.room_name(email))
            return

        try:
            tree = ET.fromstring(response)

            status = "Free"
            elems = tree.findall(common.SCHEME_TYPES + "MergedFreeBusy")
            freebusy = ''
            for elem in elems:
                freebusy = elem.text
                if '2' in freebusy:
                    status = "Busy"
                elif '3' in freebusy:
                    status = "Unavailable"
                elif '1' in freebusy:
                    status = "Tentative"

            name, size = self.rooms[email]
            self.room_info[name] = {'size': size, 'freebusy': freebusy, 'status': status, 'email' : email}

        except Exception as e:
            print "Exception querying room {}: {}".format(self.room_name(email), str(e))

    def search(self, selected_rooms=None, print_to_stdout=False):
        if selected_rooms is None:
            selected_rooms = self.rooms
        worker_threads = []

        if print_to_stdout:
            print self.user + " searching for a room from " + self.start_time + " to " + self.end_time + ":"

        xml_template = open("getavailibility_template.xml", "r").read()
        xml = Template(xml_template)

        for email in selected_rooms:
            data = unicode(xml.substitute(timezone=self.timezone,
                                          email=email,
                                          starttime=self.start_time,
                                          endtime=self.end_time))

            header = "\"content-type: text/xml;charset=utf-8\""
            command = "curl --silent --header " + header \
                       + " --data '" + data \
                       + "' --ntlm " \
                       + "-u "+ self.user + ":" + base64.b64decode(urllib.unquote(self.password)) \
                       + " " + common.URL

            thread = threading.Thread(target=self._query, args=(command, email, print_to_stdout))
            thread.start()
            worker_threads.append(thread)

        for thread in worker_threads:
            thread.join()

        if print_to_stdout:
            print "-" * 120
            print "{0:40s} {1:64s} {2:20s}".format("Status", "Room", "Email")
            print "-" * 120
            for name, info in self.room_info.iteritems():
                print "{0:40s} {1:64s} {2:20s}".format(info['status'] + '-' + info['freebusy'], name, info['email'])
            print "-" * 120
        return self.room_info

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="user name for exchange/outlook", required=True)
    parser.add_argument("-prefix", "--prefix",
                        help="A prefix to search for. e.g. 'SJC19- SJC18-'",
                        default='')
    parser.add_argument("-start", "--starttime",
                        help="Starttime e.g. 2014-07-02T11:00:00 (default = now)",
                        default=common.TIME_NOW)
    parser.add_argument("-duration", "--duration",
                        help="Duration e.g. 1h or 15m (default = 1h)",
                        default='1h')
    parser.add_argument("-f", "--file",
                        help="csv filename with room info (default=rooms.csv).",
                        default="rooms.csv")

    args = parser.parse_args()
    args.password = base64.b64encode(getpass.getpass("Password:"))

    room_finder = AvailRoomFinder(args.user, args.password, args.starttime, args.duration, args.file)
    print room_finder.search_free(prefix=args.prefix, print_to_stdout=True)


if __name__ == '__main__':
    run()
