var buildings = ["SJC-1", "SJC-2" , "SJC-3" , "SJC-4", "SJC-5"];
var floors = ["1","2","3","4"];
var times = ["8:00", "9:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00",];

function init(){

    createCombo(buildingSelect,buildings);
    createCombo(floorSelect,floors);
    createCombo(startTimeSelect,times);
    createCombo(endTimeSelect,times);

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




