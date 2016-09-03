import exchange_api
import mock
import nose
import string

ROOM_AVAIL_XML = string.Template('<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header><h:ServerVersionInfo MajorVersion="15" MinorVersion="0" MajorBuildNumber="1210" MinorBuildNumber="2" xmlns:h="http://schemas.microsoft.com/exchange/services/2006/types" xmlns="http://schemas.microsoft.com/exchange/services/2006/types" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/></s:Header><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><GetUserAvailabilityResponse xmlns="http://schemas.microsoft.com/exchange/services/2006/messages"><FreeBusyResponseArray><FreeBusyResponse><ResponseMessage ResponseClass="Success"><ResponseCode>NoError</ResponseCode></ResponseMessage><FreeBusyView><FreeBusyViewType xmlns="http://schemas.microsoft.com/exchange/services/2006/types">DetailedMerged</FreeBusyViewType><MergedFreeBusy xmlns="http://schemas.microsoft.com/exchange/services/2006/types">$freebusy</MergedFreeBusy><WorkingHours xmlns="http://schemas.microsoft.com/exchange/services/2006/types"><TimeZone><Bias>480</Bias><StandardTime><Bias>0</Bias><Time>02:00:00</Time><DayOrder>1</DayOrder><Month>11</Month><DayOfWeek>Sunday</DayOfWeek></StandardTime><DaylightTime><Bias>-60</Bias><Time>02:00:00</Time><DayOrder>2</DayOrder><Month>3</Month><DayOfWeek>Sunday</DayOfWeek></DaylightTime></TimeZone><WorkingPeriodArray><WorkingPeriod><DayOfWeek>Sunday Monday Tuesday Wednesday Thursday Friday Saturday</DayOfWeek><StartTimeInMinutes>0</StartTimeInMinutes><EndTimeInMinutes>1439</EndTimeInMinutes></WorkingPeriod></WorkingPeriodArray></WorkingHours></FreeBusyView></FreeBusyResponse></FreeBusyResponseArray></GetUserAvailabilityResponse></s:Body></s:Envelope>')

def get_popen_mock_room_avail(mock_popen, freebusy):
    process_mock = mock.Mock()
    attrs = {'communicate.return_value': (ROOM_AVAIL_XML.substitute(freebusy=freebusy), '')}
    process_mock.configure_mock(**attrs)
    mock_popen.return_value = process_mock 

@nose.tools.raises(Exception)
@mock.patch('exchange_api.subprocess.Popen')
def test_auth_failure(mock_popen):
    get_popen_mock_room_avail(mock_popen, '')
    api = exchange_api.ExchangeApi(user="testuser", password="testpassword")
    api.find_rooms(prefix="BLAH")
    assert False

@mock.patch('exchange_api.subprocess.Popen')
def test_room_available(mock_popen):
    FREEBUSY = '0000'
    ROOM_EMAIL = 'ROOM@example.com'
    get_popen_mock_room_avail(mock_popen, FREEBUSY)

    api = exchange_api.ExchangeApi(user="testuser", password="testpassword")
    response = api.room_status(room_email=ROOM_EMAIL,
                               start_time="2014-07-02T11:00:00",
                               end_time="2014-07-02T11:00:00",
                               timezone_offset="480")

    # Keys:'freebusy', 'status', 'email'
    assert response['status'] == 'Free'
    assert response['freebusy'] == FREEBUSY
    assert response['email'] == ROOM_EMAIL

@mock.patch('exchange_api.subprocess.Popen')
def test_room_unavailable(mock_popen):
    FREEBUSY = '0022'
    ROOM_EMAIL = 'ROOM@example.com'
    get_popen_mock_room_avail(mock_popen, FREEBUSY)

    api = exchange_api.ExchangeApi(user="testuser", password="testpassword")
    response = api.room_status(room_email=ROOM_EMAIL,
                               start_time="2014-07-02T11:00:00",
                               end_time="2014-07-02T11:00:00",
                               timezone_offset="480")

    # Keys:'freebusy', 'status', 'email'
    assert response['status'] != 'Free'
    assert response['freebusy'] == FREEBUSY
    assert response['email'] == ROOM_EMAIL


