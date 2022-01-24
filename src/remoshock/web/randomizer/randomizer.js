//
// Copyright nilswinter 2020-2022. License: AGPL
// _____________________________________________

"use strict";

import "../resources/remoshock.js"
import { UIFramework } from "../resources/uiframework.js"

class Randomizer {

	#uiFramework;

	async init() {
		this.#uiFramework = new UIFramework();
		this.#uiFramework.renderAppShell("Randomizer");

		globalThis.remoshock = new Remoshock();
		await remoshock.init();
		let config = await remoshock.readRandomizer();
		this.#updateUserInterface(config);
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

	async #updateUserInterface(config) {
		this.#uiFramework.load(config);
		document.getElementById("randomizerstatus").textContent = config["status"];
	}

	async start() {
		let config = {};
		this.#uiFramework.save(document.getElementById("settings"), config);
		config = await remoshock.startRandomizer(config);
		this.#updateUserInterface(config);
	}

	async stop() {
		let config = await remoshock.stopRandomizer();
		config["status"] = "stopped"; // There is a race condition on the server
		this.#updateUserInterface(config);
	}
}

new Randomizer().init();
