//
// Copyright nilswinter 2020-2025. License: AGPL
// _____________________________________________

"use strict";

import "../resources/remoshock.js"
import { UIFramework } from "../resources/uiframework.js"

/**
 * admin interface
 */
class Admin {

	#uiFramework;

	/**
	 * initialize remoshock api, asks for the current configuration and status
	 * of the randomizer process and defines html event listeners
	 */
	async init() {
		this.#uiFramework = new UIFramework();
		this.#uiFramework.renderAppShell("Admin");

		globalThis.remoshock = new Remoshock();
		await remoshock.init();
		await this.#updateUserInterface();

		// register event handlers
		document.getElementById("restart").addEventListener("click", () => {
			this.#restart();
		})
	}

	/**
	 * fills the input elements with the current configuration,
	 * updates the run status of the randomizer process
	 *
	 * @param config configuration settings
	 */
	async #updateUserInterface() {
		let feature = remoshock.config.settings.enable_feature
		if (feature && feature.indexOf("restart") > -1) {
			document.getElementById("restart").classList.remove("hidden");
		}
		document.getElementsByTagName("body")[0].classList.remove("hidden");
	}

	/**
	 * restart the remoshock service
	 */
	async #restart() {
		await remoshock.restartServer();
		alert("Restarting server, please wait a few seconds before reloading the page.");
		window.location.reload();
	}
}

new Admin().init();
