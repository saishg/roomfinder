#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import common
import csv
import getpass
import exchange_api
import operator
import string
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class RoomFinder(object):

    def __init__(self, user, password, filename='rooms.csv', append=True):
        self.user = user
        self.filename = filename
        self.exchange_api = exchange_api.ExchangeApi(self.user, password)
        self.rooms = {}
        if append:
            self._load()

    def _load(self):
        with open(self.filename, 'r') as fhandle:
            reader = csv.reader(fhandle)
            for row in reader:
                self.rooms[row[1]] = row[0], int(row[2])

    def _search(self, prefix):
        return self.exchange_api.find_rooms(prefix=prefix)

    def search(self, prefix, deep=False):
        rooms_found = self._search(prefix)

        if deep:
            symbols = string.letters + string.digits
            for symbol in symbols:
                prefix_deep = prefix + " " + symbol
                rooms_found.update(self._search(prefix_deep))

        common.LOGGER.info("Search for prefix '%s' yielded %d rooms.", prefix, len(rooms_found))
        self.rooms.update(self._search(prefix))

    def dump(self):
        if not len(self.rooms):
            common.LOGGER.warning("No results found, check your arguments for mistakes")
            return 0

        with open(self.filename, "wb") as fhandle:
            writer = csv.writer(fhandle)
            for email, room_info in sorted(self.rooms.iteritems(), key=operator.itemgetter(1)):
                name, size = room_info
                writer.writerow([name, email, size])

        return len(self.rooms)

def run():
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
