"use strict";

function addDevice(index) {
	let device = devices[index];
	let deviceTemplate = document.getElementById("device-template");
	let clone = deviceTemplate.content.cloneNode(true);

	clone.querySelector(".device").style.backgroundColor = device.color;
	clone.querySelector(".device").dataset.device = index;
	clone.querySelector("h2").innerText = device.name;
	clone.querySelector(".power_input").value = device.power;
	clone.querySelector(".power_range").value = device.power;
	clone.querySelector(".duration_input").value = device.duration;
	clone.querySelector(".duration_input").step = device.durationIncrement;
	clone.querySelector(".duration_range").value = device.duration;
	clone.querySelector(".duration_range").step = device.durationIncrement;
	
	document.getElementById("devices").appendChild(clone);   
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function command(device, action, power, duration) {
	let token = window.location.hash.substring(7);
	let url = "/pyshock/command?token=" + escape(token)
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

async function inputHandler(e) {
	let input = e.target;
	let value = input.value;
	input.parentNode.querySelector("input[type=number]").value = value;
	input.parentNode.querySelector("input[type=range]").value = value;
}

async function clickHandler(e) {
	if (e.target.tagName != "BUTTON") {
		return;
	}
	let button = e.target;
	let device = button.parentNode.parentNode;
	let action = button.className.toUpperCase();
	let power = device.querySelector(".power_input").value;
	let duration = device.querySelector(".duration_input").value;
	
	let res = await command(device.dataset.device, action, power, duration);
	if (res.status == 200) {
		navigator.vibrate([50]);
	}
}

async function init() {
	let response = await fetch('/pyshock/config.json');
	window.devices = await response.json();
	for (let i = 0; i < devices.length; i++) {
		addDevice(i);
	}
	document.getElementById("devices").addEventListener("click", clickHandler);
	document.getElementById("devices").addEventListener("input", inputHandler);
}

init();
