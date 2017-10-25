
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
    roomNamesContainer.innerHTML = gen_html(rooms_json[0])
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

function wrap_cell(data='', h=0, color='#ff00000', index=0){
    if (!h){
        return '<td onmouseout="hide_box('+index.toString()+ ')" onmouseover="free_list('+ index.toString() +' )" height="20px" style="background-color:' + color + '">' + '<span id=' + index.toString() + ' class="hoverbox"></span>'+'</td>';
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

var busy_info = [];
function free_list(index){
    var i;
    var free_attendees = [];
    for (i in busy_info){
        if (busy_info[i]["freebusy"][index] == '1'){
            free_attendees.push(busy_info[i]["name"]);
        }
    }
    var display_names = "";
    for (i in free_attendees){
        display_names += free_attendees[i] + "</br>";
    }
    document.getElementById(index.toString()).style.display = "block";
    var x = document.getElementById(index.toString())
    x.innerHTML = display_names;
}

function hide_box(index){
    document.getElementById(index).style.display = "none";
}

function gen_html(attendees_info){
    busy_info = attendees_info[1];
    avail = attendees_info[0];
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
        cells += wrap_cell('', 0, get_color(avail[slot]), slot);
    }
    inner_html += wrap_row(cells);

    inner_html += '</table>';
    return inner_html;
}
