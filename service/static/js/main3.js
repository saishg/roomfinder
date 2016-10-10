var cities = [];
var buildings = [];
var floors = [];;
var attendees = ["1", "2", "4", "5", "6", "7", "8", "9", "10", "15", "20", "25", "30", "50", "70", "100"];
var times = ["08:00AM", "09:00AM","10:00AM","11:00AM","12:00PM","01:00PM","02:00PM","03:00PM","04:00PM","05:00PM",];
var roomNames = ["SJC19-3-ARTHUR (12) (Public)","SJC19-3-GRADUATE (8) (Public)","SJC19-3-DR. STRANGELOVE (12) (Public)","SJC19-3-WILD STRAWBERRIES (6) Video (Public)", "SJC19-3-DAZED AND CONFUSED (12)"];
var startTimeBtn, endTimeBtn;
var selectedRoom;

function init(){
    loadCitiesList();

    createCombo(buildingSelect,buildings);
    createCombo(floorSelect,floors);
    createCombo(citySelect,cities);
    createCombo(roomSizeSelect,attendees);

    citySelect.value = "San Jose";
    loadBuildingList(citySelect.value);
    buildingSelect.value = "SJC19";
    loadFloorList(buildingSelect.value);

    setTodayDate();
    createTimeRows(times);

    createAvailableRoomList(roomNames);
    startTimeBtn=timeBtn0;
    endTimeBtn=timeBtn0;

}

function createCombo(container, data) {
    var options = '';
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
}

function loadBuildingList(city) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/showbuildings?city=" + city, false);
    xmlHttp.send(null);
    buildings = JSON.parse(xmlHttp.responseText);
    createCombo(buildingSelect, buildings);
}

function createTimeRows(data) {

    for (var i = 0; i < data.length; i++) {
        tableContainer.innerHTML += "<div class='timeTableRow'><label class='timeLabel' id='timeLbl"+i+"'>"+data[i]+"</label><button class='btn btn-default tableButton' id='timeBtn"+i+"' value='"+data[i]+"' onclick='handleSelectTimeBtn(this)'> 30 mins </button></div>";
    }
}

function handleSelectTimeBtn (btn) {
    if(startTimeBtn == null) {
        startTimeBtn = btn;
        endTimeBtn = btn;
    }
    else if(startTimeBtn == endTimeBtn) {
        endTimeBtn = btn;
    }
    else {
        startTimeBtn = btn;
        endTimeBtn = btn;
    }

    var startIndex = (startTimeBtn.id).charAt(startTimeBtn.id.length-1);
    var endIndex = (endTimeBtn.id).charAt(endTimeBtn.id.length-1);
    if(startIndex > endIndex) {
        var temp = startIndex;
        startIndex = endIndex;
        endIndex = temp;
    }
    var btn;
    var lbl;
    for(var i=0 ; i<times.length ;i++) {
        btn = eval('timeBtn'+i);
        lbl = eval('timeLbl'+i);
        if(i>= startIndex && i<=endIndex) {
            btn.classList.add('tableBtnEnabled');
            lbl.classList.add('timeLabelEnabled');
        }
        else {
            btn.classList.remove('tableBtnEnabled');
            lbl.classList.remove('timeLabelEnabled');
        }

    }

}

function setTodayDate() {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1; //January is 0!

    var yyyy = today.getFullYear();
    if(dd<10){
        dd='0'+dd
    }
    if(mm<10){
        mm='0'+mm
    }
    var formattedDate = yyyy +'-' + mm +'-'+dd;

    dateInput.value = formattedDate;
}

function handleSearchBtnClick() {

    var queryString = `\?user=${userNameInput.value}\&password=${passwordb64}&buildingname=${buildingSelect.value}&floor=${floorSelect.value}&starttime=${startTimeBtn.value}&endtime=${endTimeBtn.value}&attendees=${roomSizeSelect.value}&date=${dateInput.value}&timezone=${timezone}`;
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


function createAvailableRoomList (data) {
    roomNamesContainer.innerHTML += "<div class='roomNamesRow'><h4>"+data.length+" Rooms Available</h4></div>";
    for (var i = 0; i < data.length; i++) {
        roomNamesContainer.innerHTML += "<div class='roomNamesRow'><input type='radio' name='roomRadio' value='" +data[i]+ "' onclick='handleSelectRoomBtn(this)'><label class='roomNamesRadioLbl'>"+data[i]+"</label></div>";
    }
}

function handleSelectRoomBtn (radioBtn) {
    selectedRoom = radioBtn.value;
}

function handleReserveBtnClick() {
    bookRoom(selectedRoom, selectedRoom)
}

function bookRoom(roomname, roomemail) {
    var passwordb64 = encodeURIComponent(btoa(passwordInput.value));
    var timezone = new Date().getTimezoneOffset();

    var queryString = `\?user=${userNameInput.value}\&password=${passwordb64}&roomname=${roomname}&roomemail=${roomemail}&starttime=${startTimeBtn.value}&endtime=${endTimeBtn.value}&date=${dateInput.value}&timezone=${timezone}`;
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
    roomNamesContainer = '';
    hideUserPassword();
}

function hideUserPassword() {
    userNameInput.value = "";
    passwordInput.value = "";
}

