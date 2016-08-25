var buildings = []
var floors = ["1", "2", "3", "4", "5"];
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
var sizes = ["1", "2", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "20", "23", "24", "25", "30", "36", "50", "60", "65", "68", "70", "100", "120", "410"]
var date_years = ["2016", "2017"];
var date_months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
var date_days = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                 "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                 "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
                 "31"];

function init(){
    loadBuildingNamesList();
    createCombo(buildingSelect, buildings);
    createCombo(floorSelect, floors);
    createCombo(startTimeHourSelect, times_hours);
    createCombo(startTimeMinSelect, times_mins);
    createCombo(durationHourSelect, duration_hours);
    createCombo(durationMinSelect, duration_mins);
    buildingSelect.value = "SJC19";
    floorSelect.value="3";
    durationMinSelect.value = "30m";

    var date = new Date();
    var today = date.toISOString().split('T')[0];
    document.getElementById("bookDate").setAttribute('value', today);
    document.getElementById("startTimeHourSelect").value = date.getHours();
}

function createCombo(container, data) {
    var options = '';
    for (var i = 0; i < data.length; i++) {
        container.options.add(new Option(data[i], data[i]));
    }
}

function loadBuildingNamesList() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "http://localhost:5000/showbuldings", false ); // false for synchronous request
    xmlHttp.send( null );
    buildings = JSON.parse(xmlHttp.responseText);
    //console.log(buildings);
}

//Example: http://127.0.0.1:5000/showrooms?roomname=SJC19-3&starttime=2016-08-25T09:00:00&endtime=2016-08-25T19:00:00&user=mrathor&password=****

function submitClickHandler() {
    var tableHeaderRowCount = 1;
    var rowCount = mytable.rows.length;
    for (var i = tableHeaderRowCount; i < rowCount; i++) {
        mytable.deleteRow(tableHeaderRowCount);
        console.log("clearing row number:"+i);
    }
    mytable.innerHTML = "";
    mytable.visiblity = false;

    var passwordb64 = encodeURIComponent(btoa(passwordInput.value));
    var queryString = `\?user=${userNameInput.value}\&password=${passwordb64}&buildingname=${buildingSelect.value}&floor=${floorSelect.value}&starttime=${bookDate.value}T${startTimeHourSelect.value}:${startTimeMinSelect.value}:00&duration=${durationHourSelect.value}${durationMinSelect.value}`;
    loadRooms(queryString);

}

function loadRooms(queryString) {
    var xmlHttp = new XMLHttpRequest();
    url = "http://localhost:5000/showrooms";
    url = url.concat(queryString);

    xmlHttp.open("GET", url, false); // false for synchronous request
    xmlHttp.send(null);
    if (xmlHttp.responseText.trim() != "") {
        available_rooms = JSON.parse(xmlHttp.responseText);
        showFreeRooms(available_rooms);
    }
}


function showFreeRooms(rooms_json) {
    var tbl = document.getElementById('mytable');
    for (var key in rooms_json) {
        tbl.innerHTML += "<td><link>" + key + "</link></td>";
    }
    mytable.visiblity = true;
}


