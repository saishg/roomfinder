#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APIs to communicate with the Exchange Server
"""

import ConfigParser
import pipes
import string
import subprocess
import sys
import xml.etree.ElementTree as ET

reload(sys)
sys.setdefaultencoding("utf-8")

URL = 'https://mail.{}/ews/exchange.asmx'
SCHEME_TYPES = './/{http://schemas.microsoft.com/exchange/services/2006/types}'
CURL_COMMAND = "curl --silent --header 'content-type: text/xml;charset=utf-8' --data '{data}' --ntlm -u {user}:{password} {url}"
AVAILABILITY_XML = None
RESERVE_XML = None
FIND_XML = None

class ExchangeApi(object):
    """ Class to communicate with the Exchange Server """

    def __init__(self, user, password, cfg='exchange.cfg'):
        self.user = user
        self.password = password

        config = ConfigParser.ConfigParser()
        if config.read(cfg):
            self.domain = config.get('exchange', 'domain')
            self.anon_user = config.get('exchange', 'anon_user')
            self.anon_password = config.get('exchange', 'anon_password')
        else:
            self.domain = 'example.com'
            self.anon_user = self.user
            self.anon_password = self.password

        self.url = URL.format(self.domain)
        self.command = 'curl --silent --header "content-type: text/xml;charset=utf-8"' \
                       + " --data '{data}'" \
                       + " --ntlm " \
                       + "-u {user}:{password}" \
                       + " {url}"

    def _read_template(self, filename):
        with open(filename, "r") as fhandle:
            return string.Template(fhandle.read())

    def _curl(self, post_data, user, password):
        curl_command = CURL_COMMAND.format(data=post_data,
                                           user=pipes.quote(user),
                                           password=pipes.quote(password),
                                           url=self.url)
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

        if len(self.user) and len(self.password):
            response = self._curl(data, self.user, self.password)
        else:
            response = self._curl(data, self.anon_user, self.anon_password)

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

        user_email = self.user + '@' + self.domain
        room_name = room_name.replace("'", "") # Quotes cause all sorts of errors
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

        response = self._curl(data, self.user, self.password)
        return 'Success' in response

    def _parse_room_size(self, roomname):
        try:
            return int(roomname[roomname.find('(') + 1 : roomname.find(')')])
        except ValueError:
            return 1

    def _polish(self, elem_list):
        if len(elem_list) == 0 or elem_list[0] is None or elem_list[0].text is None:
            return ""
        else:
            return elem_list[0].text
            

    def find_rooms(self, prefix):
        """ Search for rooms with names starting with specified prefix """
        global FIND_XML
        if FIND_XML is None:
            FIND_XML = self._read_template("resolvenames_template.xml")

        room_info = {}
        data = unicode(FIND_XML.substitute(name=prefix))
        if len(self.user) and len(self.password):
            response = self._curl(data, self.user, self.password)
        else:
            response = self._curl(data, self.anon_user, self.anon_password)

        tree = ET.fromstring(response)
        elems = tree.findall(SCHEME_TYPES + "Resolution")
        for elem in elems:
            email = self._polish(elem.findall(SCHEME_TYPES + "EmailAddress"))
            name = self._polish(elem.findall(SCHEME_TYPES + "DisplayName"))
            city = self._polish(elem.findall(SCHEME_TYPES + "City"))
            country = self._polish(elem.findall(SCHEME_TYPES + "CountryOrRegion"))
            if len(name) > 0 and len(email) > 0 and len(city) > 0:
                roomsize = self._parse_room_size(name)
                if roomsize:
                    room_info[name] = {"name" : name,
                                       "size" : roomsize,
                                       "email" : email,
                                       "city" : city.title(),
                                       "country" : country.title(),
                                      }
        return room_info
