#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from string import Template
from string import letters
from string import digits
import subprocess
import getpass
import xml.etree.ElementTree as ET
import argparse
import csv
import operator

URL = 'https://mail.cisco.com/ews/exchange.asmx'

def find_room_with_prefix(prefix, xml, user, password):
	rooms={}
	data = unicode(xml.substitute(name=prefix))

	header = '"content-type: text/xml;charset=utf-8"'
	command = "curl --silent --header " + header + " --data '" + data + "' --ntlm " + "-u "+ user + ":" + password + " " + URL
	response = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]

	if not response.strip():
		# something went wrong
		return rooms

	tree = ET.fromstring(response)

	elems=tree.findall(".//{http://schemas.microsoft.com/exchange/services/2006/types}Resolution")
	for elem in elems:
		email = elem.findall(".//{http://schemas.microsoft.com/exchange/services/2006/types}EmailAddress")
		name = elem.findall(".//{http://schemas.microsoft.com/exchange/services/2006/types}DisplayName")
		if len(email) > 0 and len(name) > 0:
			rooms[email[0].text] = name[0].text
	return rooms

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("prefix", nargs='+',help="A list of prefixes to search for. E.g. 'conference confi'")
	parser.add_argument("-u","--user", help="user name for exchange/outlook", required=True)
	parser.add_argument("-d","--deep", help="Attemp a deep search (takes longer).", action="store_true")
	args=parser.parse_args()

	password = getpass.getpass("Password:")
	return args.user, password, args.prefix, args.deep

def find_rooms():
	user, password, prefixes, deep = parse_args()
	query_suceeded = False

	xml_template = open("resolvenames_template.xml", "r").read()
	xml = Template(xml_template)

	rooms={}

	for prefix in prefixes:
		rooms.update(find_room_with_prefix(prefix, xml, user, password))
		print "Search for prefix '" + prefix + "' yielded " + str(len(rooms)) + " rooms."
		if len(rooms):
			query_suceeded = True
		else:
			print "Check your arguments for mistakes"
			return 1

		if deep: 
			symbols = letters + digits
			for symbol in symbols:
				prefix_deep = prefix + " " + symbol
				rooms.update(find_room_with_prefix(prefix_deep, xml, user, password))
				query_suceeded = True

			print "Deep search for prefix '" + prefix + "' yielded " + str(len(rooms)) + " rooms."

	writer = csv.writer(open("rooms.csv", "wb"))
	for item in sorted(rooms.iteritems(), key=operator.itemgetter(1)):
		writer.writerow([item[1],item[0]])
	return query_suceeded

if __name__ == '__main__':
	if find_rooms():
		exit(0)
	else:
		exit(1)
