//
// Copyright nilswinter 2020-2022. License: AGPL
// _____________________________________________

"use strict";

import "../resources/remoshock.js"
import { UIFramework } from "../resources/uiframework.js"


class Remote {
	#lastNavigatorVibrate = 0;

	constructor() {
		new UIFramework().renderAppShell("Remote");

		// register event listeners
		document.getElementById("receivers").addEventListener("click", (e) => {
			this.#clickHandler(e);
		});
		document.getElementById("receivers").addEventListener("input", (e) => {
			this.#inputHandler(e);
		});

		// initalize remoshock
		this.#init();
	}

	/**
	 * initalizes remoshock and renders the configured receivers
	 */
	async #init() {
		window.remoshock = new Remoshock();
		await remoshock.init();

		for (let i = 0; i < remoshock.config.receivers.length; i++) {
			this.addreceiver(i);
		}
	}


	/**
	 * adds a receiver to the web page
	 *
	 * @param index index number of the receiver t oadd
	 */
	addreceiver(index) {
		let receiver = remoshock.config.receivers[index];
		let receiverTemplate = document.getElementById("receiver-template");
		let clone = receiverTemplate.content.cloneNode(true);

		clone.querySelector(".receiver").style.backgroundColor = receiver.color;
		clone.querySelector(".receiver").dataset.receiver = index + 1;
		clone.querySelector("h2").innerText = receiver.name;

		// power
		clone.querySelector(".power_input").value = 5;
		clone.querySelector(".power_input").max
			= receiver.limit_shock_max_power_percent || 100;

		clone.querySelector(".power_range").value = 5;
		clone.querySelector(".power_range").max
			= receiver.limit_shock_max_power_percent || 100;

		// duration
		clone.querySelector(".duration_input").value = receiver.duration_min_ms;
		clone.querySelector(".duration_input").min = 0; // receiver.duration_min_ms;
		clone.querySelector(".duration_input").max
			= Math.min(receiver.limit_shock_max_duration_ms || 2000, 2000);
		clone.querySelector(".duration_input").step = receiver.duration_increment_ms;

		clone.querySelector(".duration_range").value = receiver.duration_min_ms;
		clone.querySelector(".duration_range").min = 0; // receiver.duration_min_ms;
		clone.querySelector(".duration_range").max
			= Math.min(receiver.limit_shock_max_duration_ms || 2000, 2000);
		clone.querySelector(".duration_range").step = receiver.duration_increment_ms;

		document.getElementById("receivers").appendChild(clone);
	}


	/**
	 * handles input events
	 */
	async #inputHandler(e) {
		e.preventDefault();

		// keep input and slider consistant
		let input = e.target;
		let value = parseInt(input.value);
		if (value < 0) {
			value = 0;
		}
		if (value > e.target.max) {
			value = e.target.max;
		}
		input.parentNode.querySelector("input[type=number]").value = value;
		input.parentNode.querySelector("input[type=range]").value = value;

		// haptic feedback 
		if (navigator.vibrate && Date.now() - this.#lastNavigatorVibrate > 100) {
			navigator.vibrate([5]);
			this.#lastNavigatorVibrate = Date.now();
		}
	}

	/**
	 * handles button presses
	 */
	async #clickHandler(e) {
		e.preventDefault();
		if (e.target.tagName != "BUTTON") {
			return;
		}
		let button = e.target;
		let receiver = button.parentNode.parentNode;
		let action = button.className.toUpperCase();
		let power = receiver.querySelector(".power_input").value;
		let duration = receiver.querySelector(".duration_input").value;

		let overlay = document.getElementById("overlay");
		overlay.classList.add("wait");

		// send command to the server
		let res = await remoshock.command(receiver.dataset.receiver, action, power, duration);

		// haptic feedback
		if (navigator.vibrate) { 
			navigator.vibrate([50]);
		}

		// error indication
		if (res.status != 200) {
			overlay.classList.add("error");
			await remoshock.sleep(500);
			overlay.classList.remove("error");
		}

		// command was processed by the server
		overlay.classList.remove("wait");
	}

}

new Remote();
