#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import base64
import common
import csv
import datetime
import exchange_api
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
        self.start_time = start_time
        self.room_info = {}
        self.timezone = timezone or common.SJ_TIME_ZONE
        self.error = None
        self.exchange_api = exchange_api.ExchangeApi(user, base64.b64decode(urllib.unquote(password)))

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

    def search_free(self, prefix, min_size=1):
        selected_rooms = {}
        for email in self.rooms:
            name, size = self.rooms[email]
            if name.startswith(prefix) and size >= min_size:
                selected_rooms[email] = (name, size)

        selected_room_info = self.search(selected_rooms)
        free_room_info = {}
        for email in selected_room_info:
            if selected_room_info[email]['status'] == 'Free':
                free_room_info[email] = selected_room_info[email]
        return free_room_info

    def _query(self, email):
        room_name, room_size = self.rooms[email]
        common.LOGGER.debug("Querying for %s", room_name)

        try:
            room_info = self.exchange_api.room_status( \
                                room_email=email,
                                start_time=self.start_time,
                                end_time=self.end_time,
                                timezone_offset=self.timezone)

            room_info['size'] = room_size
            room_info['name'] = room_name
            self.room_info[room_name] = room_info

        except Exception as e:
            common.LOGGER.warning("Exception querying room %s: %s", room_name, str(e))

    def search(self, selected_rooms=None):
        if selected_rooms is None:
            selected_rooms = self.rooms
        worker_threads = []

        common.LOGGER.info("User %s searching for a room from %s to %s", self.user, self.start_time, self.end_time)

        xml_template = open("getavailibility_template.xml", "r").read()
        xml = Template(xml_template)

        for email in selected_rooms:
            thread = threading.Thread(target=self._query, args=(email, ))
            thread.start()
            worker_threads.append(thread)

        for thread in worker_threads:
            thread.join()

            if self.error is not None:
                raise self.error

        LINE_SEPARATOR = "-" * 120 + "\n"
        OUTPUT_TABLE = LINE_SEPARATOR + \
                       "{0:40s} {1:64s} {2:20s}\n".format("Status", "Room", "Email") + \
                       LINE_SEPARATOR
        for name, info in self.room_info.iteritems():
            OUTPUT_TABLE += "{0:40s} {1:64s} {2:20s}\n".format(info['status'] + '-' + info['freebusy'], name, info['email'])
        OUTPUT_TABLE += LINE_SEPARATOR

        common.LOGGER.debug("\n%s", OUTPUT_TABLE)

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
    room_finder.search_free(prefix=args.prefix)


if __name__ == '__main__':
    run()
