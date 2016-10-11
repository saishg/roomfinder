var buildings = []
var cities = []
var floors = ["1", "2", "3", "4", "5", "Any"];
var times_hours = ["00", "01", "02","03",
                   "04", "05", "06", "07",
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

var DAYS_AHEAD = 0;

function init(){
    hideUserPassword();
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
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(getCity);
    }

    var date = new Date();
    var today = date.toISOString().split('T')[0];
    bookDate.value = today;
    var current_hour = date.getHours();
    if (current_hour < 9) {
        current_hour = "0" + current_hour
    }
    startTimeHourSelect.value = current_hour;
}

function nextDate() {
    var nextDate = new Date();
    DAYS_AHEAD += 1;
    nextDate.setDate((new Date()).getDate() + DAYS_AHEAD);
    bookDate.value = nextDate.toISOString().split('T')[0];
}

function prevDate() {
    var nextDate = new Date();
    if (DAYS_AHEAD > 0) {
        DAYS_AHEAD -= 1;
    }
    nextDate.setDate((new Date()).getDate() + DAYS_AHEAD);
    bookDate.value = nextDate.toISOString().split('T')[0];
}

function hideUserPassword() {
    userLabel.style.visibility = "hidden";
    userNameInput.style.visibility = "hidden";
    passwordLabel.style.visibility = "hidden";
    passwordInput.style.visibility = "hidden";
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

function getCity(position) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/getcity?latitude=" + position.coords.latitude + "&longitude=" + position.coords.longitude, false);
    xmlHttp.send(null);
    closestCity = JSON.parse(xmlHttp.responseText);
    if (citySelect.value != closestCity) {
        citySelect.value = closestCity;
        loadBuildingList(citySelect.value);
        loadFloorList(buildingSelect.value);
    }
}

function loadFloorList(buildingname) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/showfloors?buildingname=" + buildingname, false);
    xmlHttp.send(null);
    floors = JSON.parse(xmlHttp.responseText);
    createCombo(floorSelect, floors);
    resultMessage.innerHTML = "";
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
    hideUserPassword();

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
    if (typeof error != "undefined") {
        mytable.innerHTML += "<td>Error: " + error + "</td>";
        return;
    }

    userLabel.style.visibility = "visible";
    userNameInput.style.visibility = "visible";
    passwordLabel.style.visibility = "visible";
    passwordInput.style.visibility = "visible";
    resultMessage.innerHTML = "";
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

    if (userNameInput.value == "") {
        userNameInput.style.backgroundColor = "yellow";
    }
    else {
        userNameInput.style.backgroundColor = "";
    }

    if (passwordInput.value == "") {
        passwordInput.style.backgroundColor = "yellow";
    }
    else {
        passwordInput.style.backgroundColor = "";
    }

    if (userNameInput.value == "" || passwordInput.value == "") {
        return;
    }

    url = "/bookroom";
    url = url.concat(queryString);

    xmlHttp.open("GET", url, false); // false for synchronous request
    xmlHttp.send(null);
    mytable.innerHTML = "";
    mytable.visiblity = false;
    resultMessage.innerHTML = roomname + " " + xmlHttp.responseText;
    hideUserPassword();
}


