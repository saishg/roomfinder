#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import base64
import datetime
import getpass
import os
import subprocess
import sys
import urllib

from string import Template

PWD = os.getcwd()
URL = 'https://mail.cisco.com/ews/exchange.asmx'
SCHEME_TYPES = './/{http://schemas.microsoft.com/exchange/services/2006/types}'
TIME_NOW = datetime.datetime.now().replace(microsecond=0).isoformat()
TIME_1H_FROM_NOW = None
SJ_TIME_ZONE = "420"

reload(sys)
sys.setdefaultencoding("utf-8")

CONFIG = {
        'home' : PWD,
        'roomscsv' : PWD + '/rooms.csv',
        'roomssearchcsv' : PWD + '/roomssearch.csv',
        'availibility_template' : PWD + '/getavailibility_template.xml',
        'URL': "https://mail.cisco.com/ews/exchange.asmx",
        'rooms' :  PWD + '/allrooms.csv',
        }


class ReserveAvailRoom(object):

    def __init__(self, roomname, roomemail, user, password,
                 start_time=TIME_NOW,
                 duration='1h', timezone=SJ_TIME_ZONE):
        self.roomname = roomname
        self.roomemail = roomemail
        self.user = user
        self.password = base64.b64decode(urllib.unquote(password))
        self.start_time = start_time
        self.timezone = self._calc_timezone_str(timezone)
        
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

    def _calc_timezone_str(self, timezone):
        try:
            timezone = int(timezone)
        except ValueError:
            timezone = SJ_TIME_ZONE
        hours_offset = timezone / 60
        minutes_offset = timezone % 60
        sign = "-" if hours_offset < 0 else ""
        return "{}PT{}H{}M".format(sign, abs(hours_offset), abs(minutes_offset))

    def reserve_room(self, print_to_stdout=False):
        xml_template = open("reserve_resource_template.xml", "r").read()
        xml = Template(xml_template)
        
        useremail = self.user + '@cisco.com'
        meeting_body = '{0} booked via RoomFinder by {1}'.format(self.roomname, useremail)
        subject = 'RoomFinder: {0}'.format(self.roomname)

        data = unicode(xml.substitute(resourceemail=self.roomemail,
                                      useremail=useremail,
                                      subject=subject,
                                      starttime=self.start_time,
                                      endtime=self.end_time,
                                      meeting_body=meeting_body,
                                      conf_room=self.roomname,
                                      timezone=self.timezone,
                                      ))

        header = "\"content-type: text/xml;charset=utf-8\""
        command = "curl --silent --header " + header \
                       + " --data '" + data \
                       + "' --ntlm " \
                       + "-u "+ self.user + ":" + self.password \
                       + " " + URL
        response = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
        return response

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

    parser.add_argument("-r", "--room",
                        help="Name of conf room",
                        required=True)

    args = parser.parse_args()
    args.password = getpass.getpass("Password:")

    room_finder = ReserveAvailRoom(args.room, args.user, args.password, args.starttime, args.endtime, args.file)
    print room_finder.reserve_room(print_to_stdout=True)


if __name__ == '__main__':
    run()
