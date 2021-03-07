"use strict";

function addDevice(index) {
	let device = devices[index];
	let deviceTemplate = document.getElementById("device-template");
	let clone = deviceTemplate.content.cloneNode(true);

	clone.querySelector(".device").style.backgroundColor = device.backgroundColor;
	clone.querySelector(".device").dataset.device = index;
	clone.querySelector("h2").innerText = device.name;
	clone.querySelector(".power").value = device.power;
	clone.querySelector(".power").max = device.maxPower;
	clone.querySelector(".maxPower").innerText = device.maxPower;
	clone.querySelector(".duration").value = device.duration;
	clone.querySelector(".duration").step = device.durationIncrement;
	
	document.getElementById("devices").appendChild(clone);   
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function command(device, action, power, duration) {
	let token = window.location.hash.substring(7);
	let url = "/pyshock?token=" + escape(token)
            + "&device=" + escape(device)
            + "&action=" + escape(action)
            + "&power=" + escape(power)
            + "&duration=" + escape(duration);
	return fetch(url);
}
 
async function trigger() {
	await command(config.deviceIndex, "BEEP", 0, config.beepDuration);
	await sleep(config.pauseDuration);
	await command(config.deviceIndex, "ZAP", config.zapLevel, config.zapDuration);
}

async function clickHandler(e) {
	if (e.target.tagName != "BUTTON") {
		return;
	}
	let button = e.target;
	let device = button.parentNode.parentNode;
	let action = button.className.toUpperCase();
	let power = device.querySelector(".power").value;
	let duration = device.querySelector(".duration").value;
	
	console.log(action, device, power, duration);
	await  command(device.dataset.device, action, power, duration);
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
	addDevice(i);
}

document.getElementById("devices").addEventListener("click", clickHandler);
