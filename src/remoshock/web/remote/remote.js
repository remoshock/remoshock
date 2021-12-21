"use strict";

function addreceiver(index) {
	let receiver = receivers[index];
	let receiverTemplate = document.getElementById("receiver-template");
	let clone = receiverTemplate.content.cloneNode(true);

	clone.querySelector(".receiver").style.backgroundColor = receiver.color;
	clone.querySelector(".receiver").dataset.receiver = index + 1;
	clone.querySelector("h2").innerText = receiver.name;
	clone.querySelector(".power_input").value = 5;
	clone.querySelector(".power_range").value = 5;
	clone.querySelector(".duration_input").value = receiver.duration_min_ms;
	clone.querySelector(".duration_input").min = 0; // receiver.duration_min_ms;
	clone.querySelector(".duration_input").step = receiver.duration_increment_ms;
	clone.querySelector(".duration_range").value = receiver.duration_min_ms;
	clone.querySelector(".duration_range").min = 0; // receiver.duration_min_ms;
	clone.querySelector(".duration_range").step = receiver.duration_increment_ms;

	document.getElementById("receivers").appendChild(clone);   
}


let lastNavigatorVibrate = 0;
async function inputHandler(e) {
	let input = e.target;
	let value = input.value;
	input.parentNode.querySelector("input[type=number]").value = value;
	input.parentNode.querySelector("input[type=range]").value = value;
	if (navigator.vibrate && Date.now() - lastNavigatorVibrate > 100) {
		navigator.vibrate([5]);
		lastNavigatorVibrate = Date.now();
	}
}

async function clickHandler(e) {
	if (e.target.tagName != "BUTTON") {
		return;
	}
	let button = e.target;
	let receiver = button.parentNode.parentNode;
	let action = button.className.toUpperCase();
	let power = receiver.querySelector(".power_input").value;
	let duration = receiver.querySelector(".duration_input").value;
	
	let res = await remoshock.command(receiver.dataset.receiver, action, power, duration);
	if (res.status == 200 && navigator.vibrate) {
		navigator.vibrate([50]);
	}
}

async function init() {
	window.remoshock = new Remoshock();
	await remoshock.init();

	window.receivers = remoshock.config.receivers;
	for (let i = 0; i < receivers.length; i++) {
		addreceiver(i);
	}
	document.getElementById("receivers").addEventListener("click", clickHandler);
	document.getElementById("receivers").addEventListener("input", inputHandler);
}

init();
