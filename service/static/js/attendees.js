
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

function wrap_row(cells) {
    return '<tr>' + cells + '</tr>';
}

function wrap_cell(data='', h=0, color='#ff00000'){
    if (!h){
        return '<td height="20px" style="background-color:' + color + '">' + data + '</td>';
    } else {
        return '<th>' + data + '</th>';
    }
}
var colors = ['#F0F8FF', '#87CEFA', '#1E90FF', '#0000FF'];
function get_color(factor){
    if (factor <= 50){
        return colors[0];
    } else if (factor < 75 && factor > 50){
        return colors[1];
    } else if (factor >= 75 && factor <= 99){
        return colors[2];
    } else {
        return colors[3];
    }
}

function gen_html(avail){
    var inner_html = '<table border=1>';
    var hrs = [9,10,11,12,13,14,15,16];
    var mins = [":00", ":15", ":30", ":45"];
    var cells = "";
    var x,y;
    for (i in hrs){
        for (j in mins){
            cells += wrap_cell(hrs[i] + mins[j], 1);
        }
    }
    inner_html += wrap_row(cells);

    cells = "";
    for (slot in avail){
        cells += wrap_cell('', 0, get_color(avail[slot]));
    }
    inner_html += wrap_row(cells);

    inner_html += '</table>';
    return inner_html;
}
