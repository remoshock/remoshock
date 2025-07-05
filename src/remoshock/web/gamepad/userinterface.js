//
// Copyright nilswinter 2020-2022. License: AGPL
// _____________________________________________

"use strict";

import "/resources/remoshock.js"
import "./simon-ruleset.js";
import "./walk-ruleset.js";
import { GamepadManager } from "./gamepad.js";
import { UIFramework } from "../resources/uiframework.js"


/**
 * user interface
 */
export class UserInterface {
	#MAX_BUTTONS = 17;

	#uiFramework;
	#appConfig;
	#gamepadManager;
	#ruleset;
	active = false;
	#wakeLock;

	constructor() {
		this.#uiFramework = new UIFramework();
		this.#uiFramework.renderAppShell("Gamepad");
		document.getElementById("mapping").addEventListener("click", () => {
			window.location = "/gamepad/mapping.html";
		});
		document.getElementById("start").addEventListener("click", () => {
			this.start();
		});
		document.getElementById("stop").addEventListener("click", () => {
			this.stop();
		});
		
		document.addEventListener('visibilitychange', () => {
			this.#onVisibilityChange();
		});
		this.init();
	}


	async init() {
		globalThis.remoshock = new Remoshock();
		await remoshock.init();
		console.log(remoshock.config);
		this.#appConfig = remoshock.config.applications.gamepad;

		if (!this.#appConfig) {
			this.#appConfig = {};
		}

		this.#appConfig.ruleset     = this.#appConfig.ruleset     || "simon";
		this.#appConfig.immune_ms   = this.#appConfig.immune_ms   || "3000";
		this.#appConfig.reaction_ms = this.#appConfig.reaction_ms || "1000";
		this.#appConfig.pick_interval_s = this.#appConfig.pick_interval_s || "15";
		this.#appConfig.action      = this.#appConfig.action      || "BEEPSHOCK";
		this.#appConfig.receiver    = this.#appConfig.receiver    || "1";
		this.#appConfig.shock_power_percent = this.#appConfig.shock_power_percent || "10";
		this.#appConfig.duration_ms  = this.#appConfig.duration_ms  || "500";
		this.#appConfig.play_buttons = this.#appConfig.play_buttons || "1 3 5 7 9 10 11 12";
		this.#appConfig.hold_buttons = this.#appConfig.hold_buttons || "15 16";
		this.#appConfig.runtime_min  = this.#appConfig.runtime_min  || "10";
		this.#appConfig.show_timer   = this.#appConfig.show_timer  || "1";

		let buttonMappings = remoshock.config.settings["gamepad-mapping"] || {};
		this.#uiFramework.load(this.#appConfig);
		this.#gamepadManager = new GamepadManager(this, buttonMappings);
		let rulesetClass = window.rulesets[this.#appConfig.ruleset];
		this.#ruleset = new rulesetClass(this.#appConfig, this, this.#gamepadManager);
	}


	/**
	 * aquire the wake lock again after the user switched to this browser tab again,
	 * if we had the wake lock before they left
	 */
	async #onVisibilityChange() {
		if (this.#wakeLock !== undefined && document.visibilityState === 'visible') {
			this.#wakeLock = await navigator.wakeLock.request('screen');
		}
	}


	/**
	 * event handler
	 */
	onGamepadReady() {
		this.#showConfiguredGamepad();
		setInterval(() => {
			this.#gameloop();
		}, 1);
		document.getElementById("start").classList.remove("hidden");
		document.getElementById("complianceStatus").innerText = "";
	}


	/**
	 * configures the gamepad on screen by hiding missing buttons
	 */
	#showConfiguredGamepad() {
		for (let i = 0; i < this.#MAX_BUTTONS; i++) {
			document.getElementById("b" + i).classList.add("hidden");
		}
		for (let button of this.#gamepadManager.buttons) {
			document.getElementById("b" + button.uiIndex).classList.remove("hidden");
		}
	}


	/**
	 * indicates the button state on the user interface
	 */
	displayButtonState() {
		for (let button of this.#gamepadManager.buttons) {
			if (button.isPressed()) {
				document.getElementById("t" + button.uiIndex).classList.add("pressed");
			} else {
				document.getElementById("t" + button.uiIndex).classList.remove("pressed");
			}
			if (button.desiredButtonStatus) {
				document.getElementById("b" + button.uiIndex).classList.add("desired");
			} else {
				document.getElementById("b" + button.uiIndex).classList.remove("desired");
			}
		}
	}


	/**
	 * starts the game
	 */
	async start() {
		this.#uiFramework.save(document.getElementById("settings"), this.#appConfig);

		document.getElementById("settings").classList.add("hidden")
		document.getElementById("start").classList.add("hidden")
		document.getElementById("stop").classList.remove("hidden")
		this.showInformation("");
		this.active = true;
		this.#ruleset.start();
		if ('wakeLock' in navigator) {
			this.#wakeLock = await navigator.wakeLock.request('screen');
		}
	}


	/**
	 * ends the game
	 */
	async stop() {
		this.active = false;
		this.#ruleset.stop();
		document.getElementById("settings").classList.remove("hidden")
		document.getElementById("start").classList.remove("hidden")
		document.getElementById("stop").classList.add("hidden")
		this.showInformation("inactive");
		if ('wakeLock' in navigator && this.#wakeLock) {
			await this.#wakeLock.release();
			this.#wakeLock = undefined;
		}
		this.#gamepadManager.resetAllDesiredButtonStatus()
		this.displayButtonState();
	}


	/**
	 * updates the status information
	 *
	 * @param message message to show
	 */
	showInformation(message) {
		document.getElementById("complianceStatus").innerText = message;
	}


	/**
	 * indicates a status
	 *
	 * @param indication status to indicate (e. g. "punishing")
	 */
	indicate(indication) {
		let body = document.getElementsByTagName("body")[0];
		body.classList.add(indication);
	}


	/**
	 * stops indicating a status
	 *
	 * @param indication status to no longer indicate (e. g. "punishing")
	 */
	stopIndicating(indication) {
		let body = document.getElementsByTagName("body")[0];
		body.classList.remove(indication);
	}


	/**
	 * updates the display of button status.
	 * Note: game logic is implemented in rulesets.js
	 */
	#gameloop() {
		if (!this.#gamepadManager.changesPressent()) {
			return;
		}
		this.displayButtonState();
	}
}

new UserInterface();