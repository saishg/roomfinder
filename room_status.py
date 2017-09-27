#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APIs to query an Exchange Server for availability status of rooms
"""

import argparse
import sys

import common
from exchange_api import ExchangeApi

reload(sys)
sys.setdefaultencoding("utf-8")

SEPARATOR = "-" * 120 + "\n"
TABLE_FORMAT = "{0:40s} {1:64s} {2:20s}\n"
TABLE_HEADER = SEPARATOR + TABLE_FORMAT.format("Status", "Room", "Email") + SEPARATOR

class RoomStatus(object):
    """ Class to query an Exchange Server for status of specified room """

    def __init__(self):
        self.start_time = common.TIME_NOW
        self.end_time = common.end_time(self.start_time, "15m")
        self.room_info = {}
        self.timezone = common.SJ_TIME_ZONE
        self.error = None
        self.exchange_api = ExchangeApi('', '')

    def status(self, room_email):
        common.LOGGER.debug("Querying for %s", room_email)

        try:
            if '@' not in room_email:
                room_info = self.exchange_api.find_rooms(prefix=room_email)
                if not room_info:
                    raise Exception("No room with that name")
                room_email = room_info.keys()[0]["email"]

            room_info = self.exchange_api.room_status( \
                                room_email=room_email,
                                start_time=self.start_time,
                                end_time=self.end_time,
                                timezone_offset=self.timezone)

            return room_info
        except Exception as exception:
            self.error = exception
            common.LOGGER.warning("Exception querying room %s: %s", room_email, str(exception))
            return {}

def run():
    """ Parse command-line arguments and invoke room availability finder """
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--roomemail", help="e-mail address of the room", required=True)

    args = parser.parse_args()
    room = RoomStatus()
    print room.status(args.roomemail)


if __name__ == '__main__':
    run()
