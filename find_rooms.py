#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import xml.etree.ElementTree as ET
import argparse
import csv
import operator
import subprocess
import sys

from string import Template
from string import letters
from string import digits

URL = 'https://mail.cisco.com/ews/exchange.asmx'
SCHEME_TYPES = './/{http://schemas.microsoft.com/exchange/services/2006/types}'

reload(sys)
sys.setdefaultencoding("utf-8")

class RoomFinder(object):

    def __init__(self, user, password):
        self.user = user
        self.password = password
        xml_template = open("resolvenames_template.xml", "r").read()
        self.xml = Template(xml_template)
        self.rooms = {}

    def _search(self, prefix):
        tmp_rooms = {}
        data = unicode(self.xml.substitute(name=prefix))

        header = '"content-type: text/xml;charset=utf-8"'
        command = "curl --silent --header " + header \
                   + " --data '" + data \
                   + "' --ntlm " \
                   +  "-u "+ self.user + ":" + self.password \
                   + " " + URL
        response = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]

        if not response.strip():
            # something went wrong
            return tmp_rooms

        tree = ET.fromstring(response)

        elems = tree.findall(SCHEME_TYPES + "Resolution")
        for elem in elems:
            email = elem.findall(SCHEME_TYPES + "EmailAddress")
            name = elem.findall(SCHEME_TYPES + "DisplayName")
            if len(email) and len(name):
                roomsize = self.room_size(name[0].text)
                if roomsize:
                    tmp_rooms[email[0].text] = (name[0].text, roomsize)
        return tmp_rooms

    def search(self, prefix, deep=False):
        rooms_found = self._search(prefix)

        if deep:
            symbols = letters + digits
            for symbol in symbols:
                prefix_deep = prefix + " " + symbol
                rooms_found.update(self._search(prefix_deep))

        print "Search for prefix '" + prefix + "' yielded " + str(len(rooms_found)) + " rooms."
        self.rooms.update(self._search(prefix))

    def room_size(self, roomname):
        try:
            return int(roomname[roomname.find('(') + 1 : roomname.find(')')])
        except ValueError:
            return 0

    def dump(self, filename='rooms.csv'):
        if not len(self.rooms):
            print "Check your arguments for mistakes"
            return 0

        with open(filename, "wb") as fhandle:
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
