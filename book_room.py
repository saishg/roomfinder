#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import base64
import common
import datetime
import exchange_api
import getpass
import sys
import urllib

reload(sys)
sys.setdefaultencoding("utf-8")

class ReserveAvailRoom(object):

    def __init__(self, roomname, roomemail, user, password,
                 start_time=common.TIME_NOW,
                 duration='1h', timezone=common.SJ_TIME_ZONE):
        self.roomname = roomname
        self.roomemail = roomemail
        self.user = user
        self.start_time = start_time
        self.timezone = self._calc_timezone_str(timezone)
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

    def _calc_timezone_str(self, timezone):
        try:
            timezone = int(timezone)
        except ValueError:
            timezone = common.SJ_TIME_ZONE
        hours_offset = timezone / 60
        minutes_offset = timezone % 60
        sign = "-" if hours_offset < 0 else ""
        return "{}PT{}H{}M".format(sign, abs(hours_offset), abs(minutes_offset))

    def reserve_room(self):
        response = self.exchange_api.reserve_room( \
                            room_email=self.roomemail,
                            room_name=self.roomname,
                            start_time=self.start_time,
                            end_time=self.end_time,
                            timezone_offset=self.timezone)
        return response

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="user name for exchange/outlook", required=True)
    parser.add_argument("-start", "--starttime",
                        help="Starttime e.g. 2014-07-02T11:00:00 (default = now)",
                        default=common.TIME_NOW)
    parser.add_argument("-end", "--endtime",
                        help="Endtime e.g. 2014-07-02T12:00:00 (default = now+1h)",
                        default=common.TIME_1H_FROM_NOW)
    parser.add_argument("-f", "--file",
                        help="csv filename with room info (default=rooms.csv).",
                        default="rooms.csv")

    parser.add_argument("-r", "--room",
                        help="Name of conf room",
                        required=True)

    args = parser.parse_args()
    args.password = getpass.getpass("Password:")

    room_finder = ReserveAvailRoom(args.room, args.user, args.password, args.starttime, args.endtime, args.file)
    room_finder.reserve_room()


if __name__ == '__main__':
    run()
