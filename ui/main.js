var buildings = ["SJC02", "SJC03", "SJC04", "SJC05",
                 "SJC06", "SJC07", "SJC08", "SJC09",
                 "SJC10", "SJC11", "SJC12", "SJC13",
                 "SJC14", "SJC15", "SJC16", "SJC17",
                 "SJC18", "SJC19", "SJC20", "SJC21",
                 "SJC22", "SJC23", "SJC24", "SJC28",
                 "SJC29", "SJC30", "SJC31", "SJC32",
                 "SJCA", "SJCB", "SJCD", "SJCI", "SJCJ", "SJCK",
                 "SJCL", "SJCM", "SJCMR1", "SJCMR3", "SJCN",
                 "SJCO", "SJCP", "SJCPLM01", "SJCQ", "SJCSYC02"]
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
var duration_mins = ["", "15m", "30m","45m"];
var sizes = ["1", "2", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "20", "23", "24", "25", "30", "36", "50", "60", "65", "68", "70", "100", "120", "410"]


function init(){

    createCombo(buildingSelect, buildings);
    createCombo(floorSelect, floors);
    createCombo(startTimeHourSelect, times_hours);
    createCombo(startTimeMinSelect, times_mins);
    createCombo(durationHourSelect, duration_hours);
    createCombo(durationMinSelect, duration_mins);
    createCombo(roomSizeSelect, sizes);

}

function createCombo(container, data) {
    var options = '';
    for (var i = 0; i < data.length; i++) {
        container.options.add(new Option(data[i], data[i]));
    }
}

function submitClickHandler() {

    var queryString = `?userName=${userNameInput.value}&password=${passwordInput.value}&buildingName=${buildingSelect.value}&floor=${floorSelect.value}&startTime=${startTimeSelect.value}&endTime=${endTimeSelect.value}`;
    loadRooms(queryString);
    //console.log(queryString);
}

function loadRooms(postData) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            //document.getElementById("demo").innerHTML = xhttp.responseText;
            console.log(xhttp.responseText)
        }
    };
    xhttp.open("POST", "http://www.w3schools.com/ajax/demo_post2.asp", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(postData);
}




