//
// Copyright nilswinter 2020-2022. License: AGPL
// _____________________________________________

"use strict";

import "../resources/remoshock.js"
import { UIFramework } from "../resources/uiframework.js"

/**
 * configuration interface for the randomizer
 */
class Randomizer {

	#uiFramework;
	#numberOfReceivers

	/**
	 * initialize remoshock api, asks for the current configuration and status
	 * of the randomizer process and defines html event listeners
	 */
	async init() {
		this.#uiFramework = new UIFramework();
		this.#uiFramework.renderAppShell("Randomizer");

		globalThis.remoshock = new Remoshock();
		await remoshock.init();
		this.#numberOfReceivers = remoshock.config.receivers.length;
		for (let i = 1; i <= this.#numberOfReceivers; i++) {
			this.addReceiver(i);
		}
		let config = await remoshock.readRandomizer();
		this.#updateUserInterface(config);

		// register event handlers
		document.getElementById("settings").addEventListener("change", (event) => {
			this.#validateInput(event);
		})
		document.getElementById("start").addEventListener("click", () => {
			this.start();
		})
		document.getElementById("stop").addEventListener("click", () => {
			this.stop();
		})
	}

	/**
	 * adds a receiver to the web page
	 *
	 * @param index index number of the receiver t oadd
	 */
	addReceiver(index) {
		let receiverTemplate = document.getElementById("receiver-template");
		let clone = receiverTemplate.content.cloneNode(true);
		clone.querySelector("legend").innerText = "Receiver " + remoshock.config.receivers[index - 1].name;
		let inputs = clone.querySelectorAll("input");
		for (let input of inputs) {
			input.setAttribute("id", "r" + index + "." + input.getAttribute("id"))
		}
		let labels = clone.querySelectorAll("label");
		for (let label of labels) {
			label.setAttribute("for", "r" + index + "." + label.getAttribute("for"))
		}
		document.getElementById("receivers").appendChild(clone);
	}


	/**
	 * validates input fields
	 *
	 * @param event change event
	 */
	#validateInput(event) {
		let id = event.target.id;
		let minId = id.replace("_max_", "_min_");
		let maxId = id.replace("_min_", "_max_");
		if (minId == maxId) {
			// not part of a min-max-pair
			return;
		}

		let minElement = document.getElementById(minId);
		let maxElement = document.getElementById(maxId);
		
		if (parseInt(minElement.value, 10) > parseInt(maxElement.value, 10)) {
			minElement.setCustomValidity("Min value must be smaller than max value.");
			maxElement.setCustomValidity("Min value must be smaller than max value.");
		} else {
			minElement.setCustomValidity("");
			maxElement.setCustomValidity("");
		}

		// Check receiver specific configuration against default configuration
		let pos = id.indexOf(".");
		if (pos > -1)  {
			id = id.substring(pos + 1);
		}
		minId = id.replace("_max_", "_min_");
		maxId = id.replace("_min_", "_max_");
		minElement = document.getElementById(minId);
		maxElement = document.getElementById(maxId);
		for (let i = 1; i <= this.#numberOfReceivers; i++) {
			let receiverMinElement = document.getElementById("r" + i + "."+ minId);
			let receiverMaxElement = document.getElementById("r" + i + "."+ maxId);
			if (!receiverMinElement) {
				// no a receiver specifict configuration setting
				return;
			}
			
			let minValue = parseInt(receiverMinElement.value || minElement.value, 10);
			let maxValue = parseInt(receiverMaxElement.value || maxElement.value, 10);
			if (parseInt(receiverMinElement.value, 10) > maxValue)  {
				receiverMinElement.setCustomValidity("Min value must be smaller than max value.");
			} else {
				receiverMinElement.setCustomValidity("");
			}
			if (minValue > parseInt(receiverMaxElement.value, 10))  {
				receiverMaxElement.setCustomValidity("Min value must be smaller than max value.");
			} else {
				receiverMaxElement.setCustomValidity("");
			}
			
		}

	}

	/**
	 * fills the input elements with the current configuration,
	 * updates the run status of the randomizer process
	 *
	 * @param config configuration settings
	 */
	async #updateUserInterface(config) {
		this.#uiFramework.load(config);
		document.getElementById("randomizerstatus").textContent = config["status"];
		document.getElementsByTagName("body")[0].classList.remove("hidden");
		if (this.#nonEmptyInput(config, document.getElementById("receivers"))) {
			document.getElementById("receiver-details").open = true;
		}
	}

	#nonEmptyInput(config, parent) {
		let inputs = parent.querySelectorAll("input");
		for (let input of inputs) {
			if (input.id.endsWith("probability_weight")) {
				if (input.value.length !== 0 || config["probability_weight"] != 1) {
					if (input.value != 1) {
						return true;
					}
				}
			} else {
				if (input.value.length > 0) {
					return true;
				}
			}
		}
		return false;
	}


	/**
	 * starts the randomizer, after validating configuration settings
	 */
	async start() {
		if (!document.getElementById("settings").checkValidity()) {
			alert("Validation error\n\nPlease correct your settings.");
			return;
		}
		let config = {};
		this.#uiFramework.save(document.getElementById("settings"), config);
		config["skip_startup_beeps"] = !document.getElementById("startup_beeps").checked;
		config = await remoshock.startRandomizer(config);
		this.#updateUserInterface(config);
	}


	/**
	 * stops the randomizer process
	 */
	async stop() {
		let config = await remoshock.stopRandomizer();
		config["status"] = "stopped"; // There is a race condition on the server
		this.#updateUserInterface(config);
	}
}

new Randomizer().init();
