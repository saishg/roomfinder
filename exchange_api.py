#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common
import pipes
import string
import subprocess
import sys
import xml.etree.ElementTree as ET

reload(sys)
sys.setdefaultencoding("utf-8")

AVAILABILITY_XML = None

class ExchangeApi(object):

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def _read_template(self, filename):
        with open(filename, "r") as fhandle:
            return string.Template(fhandle.read())

    def is_room_available(self, room_email, start_time, end_time, timezone_offset):
        global AVAILABILITY_XML
        if AVAILABILITY_XML is None:
            AVAILABILITY_XML = self._read_template("getavailibility_template.xml")

        data = unicode(AVAILABILITY_XML.substitute(timezone=timezone_offset,
                                                   email=room_email,
                                                   starttime=start_time,
                                                   endtime=end_time))

        command = 'curl --silent --header "content-type: text/xml;charset=utf-8"' \
                   + " --data '" + data \
                   + "' --ntlm " \
                   + "-u " + pipes.quote(self.user) + ":" + pipes.quote(self.password) \
                   + " " + common.URL

        response = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
        if not response:
            raise Exception("Authentication failure")

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

        return {'freebusy': freebusy, 'status': status, 'email' : room_email,}
