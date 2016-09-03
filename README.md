roomfinder
==========

Python scripts for finding free conference rooms from a Microsoft Exchange Server.

Requirements:

 - curl
 - Python 2.7
 - Access to Exchange Web Service (EWS) API of a Microsoft Exchange Server 2010

Before running on the command-line, edit 'exchange_api.py' and modify your DOMAIN
to your organization's domain e.g. 'example.com', so that the URL  points to
your Microsoft Exchange Server, e.g. 'https://mail.example.com/ews/exchange.asmx'

Command-line Usage:

	$ python find_rooms.py -h
	usage: find_rooms.py [-h] -u USER [-d] prefix [prefix ...]

	positional arguments:
	  prefix                A list of prefixes to search for. E.g. 'conference
	                        confi'

	optional arguments:
	  -h, --help            show this help message and exit
	  -u USER, --user USER  user name for exchange/outlook
	  -d, --deep            Attemp a deep search (takes longer).


Example:

	$ python find_rooms.py SJC19 -u sgersapp
	Password:

This will create a CSV file `rooms.csv` holding a list of all rooms found with the prefix `SJC19` in their display names.

After doing so, you can check the status for each of the rooms by calling

	$ python find_available_room.py -h
	usage: find_available_room.py [-h] -u USER [-start STARTTIME]
                                  [-end ENDTIME] [-f FILE]

	optional arguments:
	  -h, --help            show this help message and exit
	  -u USER, --user USER  user name for exchange/outlook
	  -prefix PREFIX, --prefix PREFIX
	                        A prefix to search for. e.g. 'SJC19 SJC18'
	  -start STARTTIME, --starttime STARTTIME
	                        Starttime e.g. 2014-07-02T11:00:00 (default = now)
	  -duration DURATION, --duration DURATION
	                        Duration e.g. 1h or 15m (default = 1h)
	  -f FILE, --file FILE  csv filename with room info (default=rooms.csv).


Example:

	$ python find_available_room.py -u sgersapp -start 2014-07-03T13:00:00 -duration 1h

Results are logged to the log file (default: access.log)

Eventually, you can reserve a rooms by calling

	$ python book_room.py -h
	usage: book_room.py [-h] -u USER [-start STARTTIME] [-d DURATION] -e ROOMEMAIL
						-r ROOMNAME

	optional arguments:
	  -h, --help            show this help message and exit
	  -u USER, --user USER  user name for exchange/outlook
	  -start STARTTIME, --starttime STARTTIME
	                        Starttime e.g. 2014-07-02T11:00:00 (default = now)
	  -d DURATION, --duration DURATION
	                        Duration e.g. 1h or 15m (default = 1h)
	  -e ROOMEMAIL, --roomemail ROOMEMAIL
	                        Email address of the room
	  -r ROOMNAME, --roomname ROOMNAME
	                        Name of room


Example:

	$ python book_room.py -u sgersapp -start 2014-07-03T13:00:00 -duration 1h -r SJC19-3-SAISH -e ROOM_SAISH@example.com

You will receive a confirmation email from Exchange if the reservation is accepted or rejected.

Before starting the web-app, edit 'CONFIG' and pick the number of worker threads.
Generate a certificate and private key and point CONFIG to their locations.

Web-App:

	$ ./run.sh

