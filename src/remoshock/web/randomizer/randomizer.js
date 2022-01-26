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

	/**
	 * initialize remoshock api, asks for the current configuration and status
	 * of the randomizer process and defines html event listeners
	 */
	async init() {
		this.#uiFramework = new UIFramework();
		this.#uiFramework.renderAppShell("Randomizer");

		globalThis.remoshock = new Remoshock();
		await remoshock.init();
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
		document.getElementById("reload").addEventListener("click", () => {
			window.location.reload();
		})
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
		
		if (minElement.value > maxElement.value) {
			minElement.setCustomValidity("Min value must be smaller than max value.");
			maxElement.setCustomValidity("Min value must be smaller than max value.");
		} else {
			minElement.setCustomValidity("");
			maxElement.setCustomValidity("");
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
