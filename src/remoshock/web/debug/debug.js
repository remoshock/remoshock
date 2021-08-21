"use strict";

async function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

async function command(receiver, action, power, duration) {
	let token = window.location.hash.substring(7);
	let url = "/remoshock/command?token=" + escape(token)
            + "&receiver=" + escape(receiver)
            + "&action=" + escape(action)
            + "&power=" + escape(power)
            + "&duration=" + escape(duration);
	return fetch(url);
}


async function clickHandler() {
	let output = document.getElementById("output")
	for (let i = 1; i < 1000; i++) {
		for (let j = 1; j < 4; j++) {
			output.innerText = i + " . " + j;
			await command(1, "SHOCK", 40, i);
			await sleep(3000 + (i*10));
		}
	}
}

document.getElementById("start").addEventListener("click", clickHandler);
