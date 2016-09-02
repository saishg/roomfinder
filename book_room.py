#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import base64
import common
import exchange_api
import getpass
import sys
import urllib

reload(sys)
sys.setdefaultencoding("utf-8")

class ReserveAvailRoom(object):

    def __init__(self, user, password,
                 roomname, roomemail,
                 start_time=common.TIME_NOW, duration='1h',
                 raw_password=None,
                 timezone=common.SJ_TIME_ZONE):
        self.user = user
        self.roomname = roomname
        self.roomemail = roomemail
        self.start_time = start_time
        self.timezone = self._calc_timezone_str(timezone)
        password = raw_password or base64.b64decode(urllib.unquote(password))
        self.exchange_api = exchange_api.ExchangeApi(user, password)
        self.end_time = common.end_time(self.start_time, duration)

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
    parser.add_argument("-d", "--duration",
                        help="Duration e.g. 30m (default = 1h)",
                        default='1h')
    parser.add_argument("-e", "--roomemail",
                        help="Email address of room",
                        required=True)
    parser.add_argument("-r", "--roomname",
                        help="Name of room",
                        required=True)

    args = parser.parse_args()
    args.password = base64.b64encode(getpass.getpass("Password:"))

    room_finder = ReserveAvailRoom(user=args.user, password=args.password,
                                   roomname=args.roomname, roomemail=args.roomemail,
                                   start_time=args.starttime, duration=args.duration)
    room_finder.reserve_room()


if __name__ == '__main__':
    run()
