//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________

"use strict";


/**
 * user interface
 */
class UserInterface {
	#MAX_BUTTONS = 13;
	#gamepadManager;
	#ruleset;
	active = false;

	/**
	 * @param appConfig key/value - configuration for the app
	 * @param mapping   string    - button mapping for ↖️⬆️↗️⬅️🔄➡️↙️⬇️↘️YXBA
	 */
	constructor(appConfig, mapping) {
		this.#gamepadManager = new GamepadManager(this, mapping);
		this.#ruleset = new StayRuleset(appConfig, this, this.#gamepadManager);
		document.getElementById("start").addEventListener("click", () => {
			this.start();
		});
		document.getElementById("stop").addEventListener("click", () => {
			this.stop();
		});
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

	start() {
		document.getElementById("start").classList.add("hidden")
		document.getElementById("stop").classList.remove("hidden")
		document.getElementById("complianceStatus").innerText = "";
		this.active = true;
		this.#ruleset.start();
	}

	stop() {
		this.active = false;
		this.#ruleset.stop();
		document.getElementById("start").classList.remove("hidden")
		document.getElementById("stop").classList.add("hidden")
		document.getElementById("complianceStatus").innerText = "inactive";
	}

	#gameloop() {
		if (!this.#gamepadManager.changesPressent()) {
			return;
		}
		this.displayButtonState();
	}
}

async function init() {
	window.remoshock = new Remoshock();
	await remoshock.init();
	console.log(remoshock.config);
	// let buttonMapping = "    * 7- * 6- * 6+ * 7+ *, 3 2 1 0";   // xbox
	let buttonMapping = "2 5- 1 4- * 4+ 3 5+ 0"; // select: 8, start: 9;  // DDR

	// TODO: support multipe sections
	new UserInterface(remoshock.config.applications.gamepad, buttonMapping);
}

init();


