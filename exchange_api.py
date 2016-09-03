#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APIs to communicate with the Exchange Server
"""

import pipes
import string
import subprocess
import sys
import xml.etree.ElementTree as ET

reload(sys)
sys.setdefaultencoding("utf-8")

DOMAIN = 'cisco.com'
URL = 'https://mail.{}/ews/exchange.asmx'.format(DOMAIN)
SCHEME_TYPES = './/{http://schemas.microsoft.com/exchange/services/2006/types}'
AVAILABILITY_XML = None
RESERVE_XML = None
FIND_XML = None

class ExchangeApi(object):
    """ Class to communicate with the Exchange Server """

    def __init__(self, user, password):
        self.user = user
        self.command = 'curl --silent --header "content-type: text/xml;charset=utf-8"' \
                       + " --data '{}'" \
                       + " --ntlm " \
                       + "-u " + pipes.quote(self.user) + ":" + pipes.quote(password) \
                       + " " + URL

    def _read_template(self, filename):
        with open(filename, "r") as fhandle:
            return string.Template(fhandle.read())

    def _curl(self, post_data):
        curl_command = self.command.format(post_data)
        curl_process = subprocess.Popen(curl_command,
                                        stdout=subprocess.PIPE,
                                        shell=True)
        response = curl_process.communicate()[0]
        if not response:
            raise Exception("Authentication failure")
        return response

    def room_status(self, room_email, start_time, end_time, timezone_offset):
        """ Lookup availability status of specified room """
        global AVAILABILITY_XML
        if AVAILABILITY_XML is None:
            AVAILABILITY_XML = self._read_template("getavailibility_template.xml")

        data = unicode(AVAILABILITY_XML.substitute(timezone=timezone_offset,
                                                   email=room_email,
                                                   starttime=start_time,
                                                   endtime=end_time))

        response = self._curl(data)

        tree = ET.fromstring(response)
        status = "Free"
        elems = tree.findall(SCHEME_TYPES + "MergedFreeBusy")
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

    def reserve_room(self, room_email, room_name, start_time, end_time, timezone_offset):
        """ Request reservation of specified room """
        global RESERVE_XML
        if RESERVE_XML is None:
            RESERVE_XML = self._read_template("reserve_resource_template.xml")

        user_email = self.user + '@' + DOMAIN
        meeting_body = '{0} booked via RoomFinder by {1}'.format(room_name, user_email)
        subject = 'RoomFinder: {0}'.format(room_name)

        data = unicode(RESERVE_XML.substitute(resourceemail=room_email,
                                              useremail=user_email,
                                              subject=subject,
                                              starttime=start_time,
                                              endtime=end_time,
                                              meeting_body=meeting_body,
                                              conf_room=room_name,
                                              timezone=timezone_offset,
                                             ))

        response = self._curl(data)
        return 'Success' in response

    def _parse_room_size(self, roomname):
        try:
            return int(roomname[roomname.find('(') + 1 : roomname.find(')')])
        except ValueError:
            return 0

    def find_rooms(self, prefix):
        """ Search for rooms with names starting with specified prefix """
        global FIND_XML
        if FIND_XML is None:
            FIND_XML = self._read_template("resolvenames_template.xml")

        room_info = {}
        data = unicode(FIND_XML.substitute(name=prefix))
        response = self._curl(data)

        tree = ET.fromstring(response)
        elems = tree.findall(SCHEME_TYPES + "Resolution")
        for elem in elems:
            email = elem.findall(SCHEME_TYPES + "EmailAddress")
            name = elem.findall(SCHEME_TYPES + "DisplayName")
            if len(email) and len(name):
                roomsize = self._parse_room_size(name[0].text)
                if roomsize:
                    room_info[email[0].text] = (name[0].text, roomsize)
        return room_info
