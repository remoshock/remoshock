"use strict";

function addDevice(device) {
	let deviceTemplate = document.getElementById("device-template");
	let clone = deviceTemplate.content.cloneNode(true);

	clone.querySelector(".device").style.backgroundColor = device.backgroundColor;
	clone.querySelector("h2").innerText = device.name;
	clone.querySelector(".power").value = device.power;
	clone.querySelector(".power").max = device.maxPower;
	clone.querySelector(".maxPower").innerText = device.maxPower;
	clone.querySelector(".duration").value = device.duration;
	clone.querySelector(".duration").step = device.durationIncrement;
	
	document.getElementById("devices").appendChild(clone);   
}

let devices = [
	{
		"name": "Device 1",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#FFD"
	},
	{
		"name": "Device 2",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#FFD"
	},
	{
		"name": "Device 3",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#FFD"
	},
	{
		"name": "Device 4",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#FFD"
	},
	{
		"name": "Device 5",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#EFE"
	},
	{
		"name": "Device 6",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#EFE"
	},
	{
		"name": "Device 7",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#EFE"
	},
	{
		"name": "Device 8",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#EFE"
	},
	{
		"name": "Device 9",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#EEF"
	},
	{
		"name": "Device 10",
		"power": 10,
		"duration": 500,
		"maxPower": 63,
		"durationIncrement": 250,
		"backgroundColor": "#FEE"
	}
];

for (let i = 0; i < devices.length; i++) {
	addDevice(devices[i]);
}
