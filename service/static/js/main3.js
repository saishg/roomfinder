var cities = [];
var buildings = [];
var floors = [];;
var attendees = ["1", "2", "4", "5", "6", "7", "8", "9", "10", "15", "20",
                 "25", "30", "50", "70", "100"];
//var times = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00",
//             "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00",
//             "14:00", "15:00", "16:00", "17:00", "18:00", "18:00", "19:00",
//             "20:00", "21:00", "22:00", "23:00"];
var times = ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00",
             "03:30", "04:00", "04:30", "05:00", "05:30", "06:00", "06:30",
             "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00",
             "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
             "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
             "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
             "21:00", "21:30", "22:00", "22:30", "23:00", "23:30",];
var startTimeIndex = null;
var endTimeIndex = null;

var selectedRoom;

function init(){
    loadCitiesList();

    hideUsernamePasswordFields();
    hideRoomList();

    createCombo(buildingSelect,buildings);
    createCombo(floorSelect,floors);
    createCombo(citySelect,cities);
    createCombo(roomSizeSelect,attendees);

    citySelect.value = "San Jose";
    loadBuildingList(citySelect.value);
    buildingSelect.value = "SJC19";
    loadFloorList(buildingSelect.value);
    floorSelect.value = "3";

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(getCity);
    }

    setTodayDate();
    createTimeRows(times);
    selectCurrentTime();
}

function createCombo(container, data) {
    var options = '';
    container.options.length = 0;
    for (var i=0; i < data.length; i++) {
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
}

function loadBuildingList(city) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/showbuildings?city=" + city, false);
    xmlHttp.send(null);
    buildings = JSON.parse(xmlHttp.responseText);
    createCombo(buildingSelect, buildings);
}

function createTimeRows(data) {
    var i = 0;
    for (i = 0; i < data.length; i++) {
        tableContainer.innerHTML += "<div class='timeTableRow'>";
        tableContainer.innerHTML += "<label class='timeLabel' id='timeLbl" + i + "'>" + data[i]+"</label>";
        tableContainer.innerHTML += "<button class='btn btn-default tableButton' id='timeBtn" + i + "' value='" + data[i] + "' onclick='handleTime(" + i + ")'> 30 min </button>";
        i++;
        tableContainer.innerHTML += "<label class='timeLabelHidden' id='timeLbl" + i + "'>" + data[i]+"</label>";
        tableContainer.innerHTML += "<button class='btn btn-default tableButton' id='timeBtn" + i + "' value='" + data[i] + "' onclick='handleTime(" + i + ")'> 30 min </button>";
        tableContainer.innerHTML += "</div>";
    }

    tableContainer.innerHTML += "<div class='timeTableRow'>";
    tableContainer.innerHTML += "<label class='timeLabelHidden' id='timeLbl" + i + "'" + data[0]+"</label>";
    tableContainer.innerHTML += "<button class='btn btn-default tableButton' id='timeBtn" + i + "' value='" + data[0] + "' onclick='handleTime(" + i + ")' style='visibility:hidden'> 30 min </button>";
    tableContainer.innerHTML += "</div>";
}

function handleTime(index) {
    if ((startTimeIndex == null) || (index < startTimeIndex)) {
        startTimeIndex = index;
        endTimeIndex = index;
    }
    else if (startTimeIndex == endTimeIndex) {
        endTimeIndex = index;
    }
    else {
        startTimeIndex = index;
        endTimeIndex = index;
    }

    var btn;
    var lbl;
    for (var i=0 ; i<times.length; i++) {
        btn = eval('timeBtn'+i);
        lbl = eval('timeLbl'+i);
        if (i >= startTimeIndex && i <= endTimeIndex) {
            btn.classList.add('tableBtnEnabled');
            lbl.classList.add('timeLabelEnabled');
        }
        else {
            btn.classList.remove('tableBtnEnabled');
            lbl.classList.remove('timeLabelEnabled');
        }
    }
}

function selectCurrentTime() {
    var date = new Date();
    var current_hour = date.getHours();
    var current_min = date.getMinutes();

    if (current_min < 15) {
        current_min = "00";
    }
    else if (current_min < 45) {
        current_min = "30";
    }
    else {
        current_hour++;
        current_min = "00";
    }

    if (current_hour < 10) {
        current_hour = "0" + current_hour;
    }
    else {
        current_hour = "" + current_hour;
    }

    var selectTime = current_hour + ":" + current_min;

    for (var i=0 ; i<times.length; i++) {
        if (times[i] == selectTime) {
            handleTime(i);
            eval("timeLbl" + i).scrollIntoView(true);
            break;
        }
    }
}

function setTodayDate() {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1; //January is 0!

    var yyyy = today.getFullYear();
    if (dd < 10) {
        dd = '0' + dd
    }
    if (mm < 10) {
        mm = '0' + mm
    }
    var formattedDate = yyyy +'-' + mm + '-' + dd;

    dateInput.value = formattedDate;
}

function handleSearchBtnClick() {
    var timezone = new Date().getTimezoneOffset();
    var starttime = (eval('timeBtn' + startTimeIndex)).value;
    var endtime = (eval('timeBtn' + (endTimeIndex + 1))).value;
    var queryString = `\?user=\&password=&buildingname=${buildingSelect.value}&floor=${floorSelect.value}&date=${dateInput.value}&starttime=${starttime}&endtime=${endtime}&attendees=${roomSizeSelect.value}&timezone=${timezone}`;
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
        resultMessage.innerHTML = "Error: " + error;
        return;
    }
    else {
        resultMessage.innerHTML = "";
    }

    roomNamesContainer.innerHTML = "<label class='rightDivLbl' id='selectRoomText'> 1. Select A Room </label>";
    roomNamesContainer.innerHTML += "<div class='roomNamesRow'><h4>" + Object.keys(rooms_json).length + " room(s) available</h4></div>";
    for (var key in rooms_json) {
        var roomemail = rooms_json[key]["email"];
        if (typeof roomemail != "undefined") {
            roomNamesContainer.innerHTML += "<div class='roomNamesRow'><input type='radio' name='roomRadio' value='" + key + "' onclick='handleSelectRoomBtn(this)'><label class='roomNamesRadioLbl'>" + key + "</label></div>";
        }
    }
}

function handleSelectRoomBtn (radioBtn) {
    selectedRoom = radioBtn.value;
    showUsernamePasswordFields();
}

function handleReserveBtnClick() {
    var passwordb64 = encodeURIComponent(btoa(passwordInput.value));
    var timezone = new Date().getTimezoneOffset();
    var starttime = (eval('timeBtn' + startTimeIndex)).value;
    var endtime = (eval('timeBtn' + (endTimeIndex + 1))).value;
    var queryString = `\?user=${userNameInput.value}\&password=${passwordb64}&roomname=${selectedRoom}&starttime=${starttime}&endtime=${endtime}&date=${dateInput.value}&timezone=${timezone}`;
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
    hideRoomList();
    hideUsernamePasswordFields();
	resultMessage.innerHTML = selectedRoom + " " + xmlHttp.responseText;
}

function hideRoomList() {
    roomNamesContainer.innerHTML = '';
    roomNamesContainer.style.visibility = false;
}

function showUsernamePasswordFields() {
    var userpassHTML = "<label class='rightDivLbl'> 2. Enter User name and Password </label>";
    userpassHTML += "<div><label class='userNamePswdLbl'>User name</label></div>";
    userpassHTML += "<input  type='text' id='userNameInput' class='form-control userNamePswdInputText' placeholder='User name'></input>";
    userpassHTML += "<div><label class='userNamePswdLbl'>Password</label></div>";
    userpassHTML += "<input  type='password' id='passwordInput' class='form-control userNamePswdInputText' placeholder='Password'></input>";
    userpassHTML += "<button class='btn btn-default reserveButton form-control' type='button' onclick='handleReserveBtnClick()' >Reserve</button>";

    usernamePasswordContainer.style.visibility = true;
    usernamePasswordContainer.innerHTML = userpassHTML;
}

function hideUsernamePasswordFields() {
    usernamePasswordContainer.style.visibility = false;
    usernamePasswordContainer.innerHTML = "";
}

