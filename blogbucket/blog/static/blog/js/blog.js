var req;

// Sends a new request to update the user list
function sendRequest() {
	if (window.XMLHttpRequest) {
		req = new XMLHttpRequest();
	} else {
		req = new ActiveXObject("Microsoft.XMLHTTP");
	}
	req.onreadystatechange = handleResponse;
	req.open("GET", "/blog/get-users", true);
	req.send();
}

// This function is called for each request readystatechange, it parses the XML response for the request
function handleResponse() {
	if (req.readyState != 4 || req.status != 200) {
		return;
	}

	// Removes the old user list
	var list = document.getElementById("user-list");
	if (list != null) {
	while (list.hasChildNodes()) {
		list.removeChild(list.firstChild);
	}

	//Parses the XML response to get a list of DOM nodes representing items
	var xmlData = req.responseXML;
	var users = xmlData.getElementsByTagName("item");

	// Adds each new user to the list of users
	for (var i = 0; i < users.length; i++) {
		// Parses the user id and name text from the DOM
		var id = users[i].getElementsByTagName("id")[0].textContent;
		var itemText = users[i].getElementsByTagName("text")[0].textContent;

		// Builds a new HTML list for the user list
		var newItem = document.createElement("li");
		newItem.innerHTML = "<a href=\"/blog/index/" + id + "\">" + itemText + "</a>";

		// Adds the user to the HTML user list
		list.appendChild(newItem);
	}
	}

}


window.setInterval(sendRequest, 9000);