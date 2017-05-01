#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APIs to query an Exchange Server for list of rooms
"""


import argparse
import getpass
import string
import sys

import common
import exchange_api

reload(sys)
sys.setdefaultencoding("utf-8")

class RoomFinder(object):
    """ Class to query an Exchange Server for list of rooms """

    def __init__(self, user, password, filename='rooms.csv', append=True):
        self.user = user
        self.filename = filename
        self.exchange_api = exchange_api.ExchangeApi(self.user, password)
        self.rooms = {}
        if append:
            self.rooms = common.read_room_list(self.filename)

    def _search(self, prefix):
        return self.exchange_api.find_rooms(prefix=prefix)

    def _search_to_be_deleted(self, prefix, newrooms):
        to_be_deleted = []
        for room in self.rooms:
            if room not in newrooms and room.startswith(prefix):
                to_be_deleted.append(room)
                print "--", room
        return to_be_deleted

    def search(self, prefix, deep=False):
        """ Search for rooms with names starting with specified prefix """
        rooms_found = self._search(prefix)
        to_be_deleted = self._search_to_be_deleted(prefix, rooms_found)

        if deep:
            symbols = string.letters + string.digits
            for symbol in symbols:
                prefix_deep = prefix + " " + symbol
                rooms_found.update(self._search(prefix_deep))

        common.LOGGER.info("Search for prefix '%s' yielded %d rooms.", prefix, len(rooms_found))
        self.rooms.update(rooms_found)
        for room in to_be_deleted:
            common.LOGGER.info("Deleting room '%s' room for prefix '%s'.", room, prefix)
            del self.rooms[room]

    def dump(self):
        """ Dump the results to specified file """
        if not len(self.rooms):
            common.LOGGER.warning("No results found, check your arguments for mistakes")
            return 0

        common.write_room_list(self.rooms, filename=self.filename)
        return len(self.rooms)

def run():
    """ Parse command-line arguments and invoke room finder """
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix", nargs='+', help="A prefix to search for. e.g. 'SJC19- SJC18-'")
    parser.add_argument("-u", "--user", help="user name for exchange/outlook", required=True)
    parser.add_argument("-d", "--deep", help="Attemp a deep slow search", action="store_true")
    args = parser.parse_args()

    args.password = getpass.getpass("Password:")

    finder = RoomFinder(args.user, args.password)

    for prefix in args.prefix:
        finder.search(prefix, args.deep)

    if finder.dump():
        exit(0)
    else:
        exit(1)

if __name__ == '__main__':
    run()
