//
// Copyright nilswinter 2020-2025. License: AGPL
// _____________________________________________

"use strict";

import "../resources/remoshock.js"
import { UIFramework } from "../resources/uiframework.js"

/**
 * show the log file
 */
class Log {

	#uiFramework;

	/**
	 * initialize remoshock api, asks for the current configuration and status
	 * of the randomizer process and defines html event listeners
	 */
	async init() {
		this.#uiFramework = new UIFramework();
		this.#uiFramework.renderAppShell("Log");

		globalThis.remoshock = new Remoshock();
		await remoshock.init();
		await this.#updateUserInterface();

		// register event handlers
		document.getElementById("refresh").addEventListener("click", () => {
			this.#updateUserInterface();
		})
	}

	/**
	 * fills the input elements with the current configuration,
	 * updates the run status of the randomizer process
	 *
	 * @param config configuration settings
	 */
	async #updateUserInterface() {
		let log = await remoshock.readLog();
		let logElement = document.getElementById("log");
		logElement.textContent = log;
		document.getElementsByTagName("body")[0].classList.remove("hidden");
		logElement.scrollTop = logElement.scrollHeight;
	}
}

new Log().init();
