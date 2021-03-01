"use strict";

function addDevice(device) {
	let deviceTemplate = document.getElementById("device-template");
	let clone = deviceTemplate.content.cloneNode(true);

	document.getElementById("devices").appendChild(clone);   
}

let devices = [
	{
		"name": "Device 1"
	},
	{
		"name": "Device 2"
	},
	{
		"name": "Device 3"
	},
	{
		"name": "Device 4"
	},
	{
		"name": "Device 5"
	},
	{
		"name": "Device 6"
	},
	{
		"name": "Device 7"
	},
	{
		"name": "Device 8"
	},
	{
		"name": "Device 9"
	},
	{
		"name": "Device 10"
	}
];

for (let i = 0; i < devices.length; i++) {
	addDevice(devices[i]);
}
