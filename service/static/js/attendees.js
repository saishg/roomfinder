
function init(){
    setTodayDate();
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
    var queryString = `\?emails=${attendeesList.value}&date=${dateInput.value}&timezone=${timezone}`;
    loadRooms(queryString);
}

function loadRooms(queryString) {
    var xmlHttp = new XMLHttpRequest();
    url = "/schedule";
    url = url.concat(queryString);
    console.log(url)

    xmlHttp.open("GET", url, false); // false for synchronous request
    xmlHttp.send(null);
    if (xmlHttp.responseText.trim() != "") {
        console.log(xmlHttp.responseText)
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
	resultMessage.style.display = "none";
	resultMap.style.display = "none";
    }

    roomNamesContainer.style.display = "block";
    roomNamesContainer.innerHTML = '<label class="rightDivLbl" id="selectRoomText"> 1. Select A Room </label>';
    roomNamesContainer.innerHTML += '<div class="roomNamesRow"><h4>' + Object.keys(rooms_json).length + ' room(s) available</h4></div>';
    for (var key in rooms_json) {
        var roomemail = rooms_json[key]["email"];
        if (typeof roomemail != "undefined") {
            roomNamesContainer.innerHTML += '<div class="roomNamesRow"><input type="radio" name="roomRadio" value="' + key + '" onclick="handleSelectRoomBtn(this)"><label class="roomNamesRadioLbl">' + key + '</label></div>';
        }
    }
}

function handleSelectRoomBtn (radioBtn) {
    selectedRoom = radioBtn.value;
    showUsernamePasswordFields();
}

function hideRoomList() {
    roomNamesContainer.innerHTML = '';
    roomNamesContainer.style.display = "none";
}


