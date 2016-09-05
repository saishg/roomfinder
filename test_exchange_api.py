"""
Unit Tests for exchange_api.py
"""

import string

import exchange_api
import mock
import nose

XML_KEYS = {'XML_SOAP_ENVELOPE' : 'http://schemas.xmlsoap.org/soap/envelope/',
            'XML_SCHEMA' : 'http://schemas.microsoft.com/exchange/services/2006',
            'XML_W3_SCHEMA' : 'http://www.w3.org/2001/XMLSchema',
           }

ROOM_INFO_XML = string.Template('<t:Resolution><t:Mailbox><t:Name>$room_name</t:Name><t:EmailAddress>$room_name@example.com</t:EmailAddress><t:RoutingType>SMTP</t:RoutingType><t:MailboxType>Mailbox</t:MailboxType></t:Mailbox><t:Contact><t:DisplayName>$room_name (12)</t:DisplayName><t:GivenName>ROOM</t:GivenName><t:Initials/><t:CompanyName/><t:EmailAddresses/><t:PhysicalAddresses/><t:PhoneNumbers/><t:AssistantName/><t:ContactSource>ActiveDirectory</t:ContactSource><t:Department/><t:JobTitle/><t:OfficeLocation/><t:Surname>$room_name</t:Surname></t:Contact></t:Resolution>')

FIND_ROOMS_XML = string.Template('<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="{XML_SOAP_ENVELOPE}"><s:Header><h:ServerVersionInfo xmlns:h="{XML_SCHEMA}/types" xmlns="{XML_SCHEMA}/types" xmlns:xsd="{XML_W3_SCHEMA}" xmlns:xsi="{XML_W3_SCHEMA}-instance" MajorVersion="15" MinorVersion="0" MajorBuildNumber="1210" MinorBuildNumber="2"/></s:Header><s:Body xmlns:xsi="{XML_W3_SCHEMA}-instance" xmlns:xsd="{XML_W3_SCHEMA}"><m:ResolveNamesResponse xmlns:m="{XML_SCHEMA}/messages" xmlns:t="{XML_SCHEMA}/types"><m:ResponseMessages><m:ResolveNamesResponseMessage ResponseClass="Warning"><m:MessageText>Multiple results were found.</m:MessageText><m:ResponseCode>ErrorNameResolutionMultipleResults</m:ResponseCode><m:DescriptiveLinkKey>0</m:DescriptiveLinkKey><m:ResolutionSet TotalItemsInView="$num_rooms" IncludesLastItemInRange="true">$room_info</m:ResolutionSet></m:ResolveNamesResponseMessage></m:ResponseMessages></m:ResolveNamesResponse></s:Body></s:Envelope>'.format(**XML_KEYS))

ROOM_AVAIL_XML = string.Template('<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="{XML_SOAP_ENVELOPE}"><s:Header><h:ServerVersionInfo MajorVersion="15" MinorVersion="0" MajorBuildNumber="1210" MinorBuildNumber="2" xmlns:h="{XML_SCHEMA}/types" xmlns="{XML_SCHEMA}/types" xmlns:xsd="{XML_W3_SCHEMA}" xmlns:xsi="{XML_W3_SCHEMA}-instance"/></s:Header><s:Body xmlns:xsi="{XML_W3_SCHEMA}-instance" xmlns:xsd="{XML_W3_SCHEMA}"><GetUserAvailabilityResponse xmlns="{XML_SCHEMA}/messages"><FreeBusyResponseArray><FreeBusyResponse><ResponseMessage ResponseClass="Success"><ResponseCode>NoError</ResponseCode></ResponseMessage><FreeBusyView><FreeBusyViewType xmlns="{XML_SCHEMA}/types">DetailedMerged</FreeBusyViewType><MergedFreeBusy xmlns="{XML_SCHEMA}/types">$freebusy</MergedFreeBusy><WorkingHours xmlns="{XML_SCHEMA}/types"><TimeZone><Bias>480</Bias><StandardTime><Bias>0</Bias><Time>02:00:00</Time><DayOrder>1</DayOrder><Month>11</Month><DayOfWeek>Sunday</DayOfWeek></StandardTime><DaylightTime><Bias>-60</Bias><Time>02:00:00</Time><DayOrder>2</DayOrder><Month>3</Month><DayOfWeek>Sunday</DayOfWeek></DaylightTime></TimeZone><WorkingPeriodArray><WorkingPeriod><DayOfWeek>Sunday Monday Tuesday Wednesday Thursday Friday Saturday</DayOfWeek><StartTimeInMinutes>0</StartTimeInMinutes><EndTimeInMinutes>1439</EndTimeInMinutes></WorkingPeriod></WorkingPeriodArray></WorkingHours></FreeBusyView></FreeBusyResponse></FreeBusyResponseArray></GetUserAvailabilityResponse></s:Body></s:Envelope>'.format(**XML_KEYS))

ROOM_RESERVE_XML = string.Template('<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="{XML_SOAP_ENVELOPE}"><s:Header><h:ServerVersionInfo xmlns:h="{XML_SCHEMA}/types" xmlns="{XML_SCHEMA}/types" xmlns:xsd="{XML_W3_SCHEMA}" xmlns:xsi="{XML_W3_SCHEMA}-instance" MajorVersion="15" MinorVersion="0" MajorBuildNumber="1210" MinorBuildNumber="2" Version="V2_23"/></s:Header><s:Body xmlns:xsi="{XML_W3_SCHEMA}-instance" xmlns:xsd="{XML_W3_SCHEMA}"><m:CreateItemResponse xmlns:m="{XML_SCHEMA}/messages" xmlns:t="{XML_SCHEMA}/types"><m:ResponseMessages><m:CreateItemResponseMessage ResponseClass="$result"><m:ResponseCode>NoError</m:ResponseCode><m:Items><t:CalendarItem><t:ItemId Id="AAMkADdjOTY0YWI5LWI4NzAtNGU4OC04MjAyLTgyMjFjZmFlMzhkOQBGAAAAAAA537+zip9BToctZGZWgs3IBwD/dt2bgtXgRKEhWftUlaSuAAAC3uxpAADFT7UXKH2LTLWQ1hNAo69lAAC3z5RCAAA=" ChangeKey="DwAAABYAAADFT7UXKH2LTLWQ1hNAo69lAAC34R9T"/></t:CalendarItem></m:Items></m:CreateItemResponseMessage></m:ResponseMessages></m:CreateItemResponse></s:Body></s:Envelope>'.format(**XML_KEYS))

ROOM_EMAIL = 'ROOM@example.com'
ROOM_NAME = 'ROOM'
START_TIME = "2016-11-09T11:00:00"
END_TIME = "2016-11-09T11:30:00"
TIME_ZONE_OFFSET = "480"

@nose.tools.raises(Exception)
@mock.patch('exchange_api.subprocess.Popen')
def test_auth_failure(mock_popen):
    get_popen_mock_room_avail(mock_popen, '')
    api = exchange_api.ExchangeApi(user="testuser", password="testpassword")
    api.find_rooms(prefix="ROOM")
    assert False

def get_popen_mock_find_rooms(mock_popen, room_info):
    process_mock = mock.Mock()
    attrs = {'communicate.return_value':
             (FIND_ROOMS_XML.substitute(num_rooms=len(room_info),
                                        room_info=''.join(room_info)),
              '')}
    process_mock.configure_mock(**attrs)
    mock_popen.return_value = process_mock

@mock.patch('exchange_api.subprocess.Popen')
def test_find_rooms(mock_popen):
    room1 = ROOM_INFO_XML.substitute(room_name='ROOM1')
    room2 = ROOM_INFO_XML.substitute(room_name='ROOM2')
    room3 = ROOM_INFO_XML.substitute(room_name='ROOM3')

    get_popen_mock_find_rooms(mock_popen, room_info=[room1, room2, room3])
    api = exchange_api.ExchangeApi(user="testuser", password="testpassword")
    response = api.find_rooms(prefix="ROOM")
    assert len(response) == 3
    assert response.get('ROOM1@example.com')
    assert response.get('ROOM2@example.com')
    assert response.get('ROOM3@example.com')
    assert response.get('ROOM4@example.com') is None

def get_popen_mock_room_avail(mock_popen, freebusy):
    process_mock = mock.Mock()
    attrs = {'communicate.return_value': (ROOM_AVAIL_XML.substitute(freebusy=freebusy), '')}
    process_mock.configure_mock(**attrs)
    mock_popen.return_value = process_mock

@mock.patch('exchange_api.subprocess.Popen')
def test_room_available(mock_popen):
    freebusy = '0000'
    get_popen_mock_room_avail(mock_popen, freebusy=freebusy)

    api = exchange_api.ExchangeApi(user="testuser", password="testpassword")
    response = api.room_status(room_email=ROOM_EMAIL,
                               start_time=END_TIME,
                               end_time=END_TIME,
                               timezone_offset=TIME_ZONE_OFFSET)

    # Keys:'freebusy', 'status', 'email'
    assert response['status'] == 'Free'
    assert response['freebusy'] == freebusy
    assert response['email'] == ROOM_EMAIL

@mock.patch('exchange_api.subprocess.Popen')
def test_room_unavailable(mock_popen):
    freebusy = '0022'
    get_popen_mock_room_avail(mock_popen, freebusy=freebusy)

    api = exchange_api.ExchangeApi(user="testuser", password="testpassword")
    response = api.room_status(room_email=ROOM_EMAIL,
                               start_time=START_TIME,
                               end_time=END_TIME,
                               timezone_offset=TIME_ZONE_OFFSET)

    # Keys:'freebusy', 'status', 'email'
    assert response['status'] != 'Free'
    assert response['freebusy'] == freebusy
    assert response['email'] == ROOM_EMAIL

def get_popen_mock_room_reserve(mock_popen, result):
    process_mock = mock.Mock()
    attrs = {'communicate.return_value': (ROOM_RESERVE_XML.substitute(result=result), '')}
    process_mock.configure_mock(**attrs)
    mock_popen.return_value = process_mock

@mock.patch('exchange_api.subprocess.Popen')
def test_room_reserve_success(mock_popen):
    result = 'Success'
    get_popen_mock_room_reserve(mock_popen, result)

    api = exchange_api.ExchangeApi(user="testuser", password="testpassword")
    response = api.reserve_room(room_email=ROOM_EMAIL,
                                room_name=ROOM_NAME,
                                start_time=START_TIME,
                                end_time=END_TIME,
                                timezone_offset=TIME_ZONE_OFFSET)

    assert response is True

@mock.patch('exchange_api.subprocess.Popen')
def test_room_reserve_failure(mock_popen):
    result = 'Failure'
    get_popen_mock_room_reserve(mock_popen, result)

    api = exchange_api.ExchangeApi(user="testuser", password="testpassword")
    response = api.reserve_room(room_email=ROOM_EMAIL,
                                room_name=ROOM_NAME,
                                start_time=START_TIME,
                                end_time=END_TIME,
                                timezone_offset=TIME_ZONE_OFFSET)

    assert response is False
