var buildings = []
var cities = []
var floors = ["1", "2", "3", "4", "5", "Any"];
var times_hours = ["00", "01", "02","03",
                   "4", "05", "06", "07",
                   "08", "09", "10", "11",
                   "12", "13", "14", "15",
                   "16", "17", "18", "19",
                   "20", "21", "22", "23"];
var times_mins = ["00", "15", "30","45"];
var duration_hours = ["0h", "1h", "2h","3h",
                      "4h", "5h", "6h", "7h"];
var duration_mins = ["00m", "15m", "30m","45m"];
var sizes = ["1", "2", "4", "5", "6", "7", "8", "9", "10", "15", "20", "25", "30", "50", "70", "100"];
var date_years = ["2016", "2017"];
var date_months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
var date_days = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                 "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                 "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
                 "31"];

function init(){
    loadCitiesList();
    createCombo(buildingSelect, buildings);
    createCombo(citySelect, cities);
    createCombo(floorSelect, floors);
    createCombo(roomSizeSelect, sizes);
    createCombo(startTimeHourSelect, times_hours);
    createCombo(startTimeMinSelect, times_mins);
    createCombo(durationHourSelect, duration_hours);
    createCombo(durationMinSelect, duration_mins);

    citySelect.value = "San Jose";
    loadBuildingList(citySelect.value);
    buildingSelect.value = "SJC19";
    loadFloorList(buildingSelect.value);
    floorSelect.value = "3";
    durationMinSelect.value = "30m";

    var date = new Date();
    var today = date.toISOString().split('T')[0];
    document.getElementById("bookDate").setAttribute('value', today);
    var current_hour = date.getHours();
    if (current_hour.length < 2) {
        current_hour = "0" + current_hour
    }
    document.getElementById("startTimeHourSelect").value = current_hour;
}

function createCombo(container, data) {
    var options = '';
    container.options.length = 0;
    for (var i = 0; i < data.length; i++) {
        container.options.add(new Option(data[i], data[i]));
    }
}

function loadCitiesList() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/showcities", false);
    xmlHttp.send(null);
    cities = JSON.parse(xmlHttp.responseText);
}

function loadFloorList(buildingname) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/showfloors?buildingname=" + buildingname, false);
    xmlHttp.send(null);
    floors = JSON.parse(xmlHttp.responseText);
    createCombo(floorSelect, floors);
}

function loadBuildingList(city) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/showbuildings?city=" + city, false);
    xmlHttp.send(null);
    buildings = JSON.parse(xmlHttp.responseText);
    createCombo(buildingSelect, buildings);
}

//Example: http://127.0.0.1:5000/showrooms?roomname=SJC19-3&starttime=2016-08-25T09:00:00&endtime=2016-08-25T19:00:00&user=mrathor&password=****


//Example: http://127.0.0.1:5000/showrooms?roomname=SJC19-3&starttime=2016-08-25T09:00:00&endtime=2016-08-25T19:00:00&user=mrathor&password=****

function submitClickHandler() {
    var tableHeaderRowCount = 1;
    var rowCount = mytable.rows.length;
    for (var i = tableHeaderRowCount; i < rowCount; i++) {
        mytable.deleteRow(tableHeaderRowCount);
        console.log("clearing row number:" + i);
    }
    mytable.innerHTML = "";
    mytable.visiblity = false;

    var passwordb64 = encodeURIComponent(btoa(passwordInput.value));
    var timezone = new Date().getTimezoneOffset();

    var queryString = `\?user=${userNameInput.value}\&password=${passwordb64}&buildingname=${buildingSelect.value}&floor=${floorSelect.value}&starttime=${bookDate.value}T${startTimeHourSelect.value}:${startTimeMinSelect.value}:00&duration=${durationHourSelect.value}${durationMinSelect.value}&attendees=${roomSizeSelect.value}&timezone=${timezone}`;
    loadRooms(queryString);

}

function loadRooms(queryString) {
    var xmlHttp = new XMLHttpRequest();
    url = "/showrooms";
    url = url.concat(queryString);

    xmlHttp.open("GET", url, false); // false for synchronous request
    xmlHttp.send(null);
    if (xmlHttp.responseText.trim() != "") {
        available_rooms = JSON.parse(xmlHttp.responseText);
        showFreeRooms(available_rooms);
    }
}


function showFreeRooms(rooms_json) {
    error = rooms_json["Error"];
    console.log(error);
    if (typeof error != "undefined") {
        mytable.innerHTML += "<td>Error: " + error + "</td>";
        return;
    }

    mytable.innerHTML += "<td></td><td><small>Found " + Object.keys(rooms_json).length + " rooms</small></td>";
    for (var key in rooms_json) {
        var roomemail = rooms_json[key]["email"];
        if (typeof roomemail != "undefined") {
            mytable.innerHTML += '<td><input type="submit" value="Reserve" onclick="bookRoom(\'' + key + '\' , \'' + roomemail + '\');"></td><td>' + key + '</td>';
        }
        else {
            mytable.innerHTML += '<td></td><td>' + key + '</td>';
        }
    }
    mytable.visiblity = true;
}

function bookRoom(roomname, roomemail) {
    var passwordb64 = encodeURIComponent(btoa(passwordInput.value));
    var timezone = new Date().getTimezoneOffset();

    var queryString = `\?user=${userNameInput.value}\&password=${passwordb64}&roomname=${roomname}&roomemail=${roomemail}&starttime=${bookDate.value}T${startTimeHourSelect.value}:${startTimeMinSelect.value}:00&duration=${durationHourSelect.value}${durationMinSelect.value}&timezone=${timezone}`;
    var xmlHttp = new XMLHttpRequest();

    url = "/bookroom";
    url = url.concat(queryString);

    xmlHttp.open("GET", url, false); // false for synchronous request
    xmlHttp.send(null);
	mytable.innerHTML = '<tr><td>' + roomname + " " + xmlHttp.responseText + '</td></tr>';
	
}


