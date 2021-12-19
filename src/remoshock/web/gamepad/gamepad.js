"use strict";


/**
 * @enum
 */
class ComplianceStatus {

	static get COMPLIANT() {
		return "COMPLIANT";
	}

	static get PENDING() {
		return "PENDING";
	}

	static get VIOLATED() {
		return "VIOLATED";
	}

	/**
	 * gets the worst status of the provided paramsters
	 *
	 * @param a ComplianceStatus
	 * @param b ComplianceStatus
	 */
	static worst(a, b) {
		if (a == ComplianceStatus.VIOLATED || b == ComplianceStatus.VIOLATED) {
			return ComplianceStatus.VIOLATED;
		}
	
		if (a == ComplianceStatus.PENDING || b == ComplianceStatus.PENDING) {
			return ComplianceStatus.PENDING;
		}

		return ComplianceStatus.COMPLIANT;
	}
}


/**
 * a gamepad button. This class handles both real buttons, and axis-based directional buttons.
 */
class GamepadButton {
	uiIndex = -1;
	#gamepadManager;
	#buttonIndex;
	#direction = 0;
	#lastButtonStatus = false;
	desiredButtonStatus = false;

	/**
	 * @param index          number - of the userinterface representation
	 * @param gamepadManager GamepadManager - reference to the gamepad
	 * @param buttonIndex    number - index as used by the Web GamepadAPI
	 * @param direction      number - 0 for buttons, -1 or 1 for directional buttons
	 */
	constructor(uiIndex, gamepadManager, buttonIndex, direction) {
		this.uiIndex = uiIndex;
		this.#gamepadManager = gamepadManager;
		this.#direction = direction;
		this.#buttonIndex = buttonIndex;
	}


	isPressed() {
		if (this.#direction == 0) {
			let button = this.#gamepadManager.gamepad.buttons[this.#buttonIndex]
			return button.pressed;
		} else {
			let axis = this.#gamepadManager.gamepad.axes[this.#buttonIndex];
			return axis * this.#direction > 0.5;
		}
	}

	checkComplianceStatus() {
		let status = this.isPressed();
		if (status == this.desiredButtonStatus) {
			this.#lastButtonStatus = status;
			return ComplianceStatus.COMPLIANT;
		}

		if (status == this.#lastButtonStatus) {
			return ComplianceStatus.PENDING;
		}

		return ComplianceStatus.VIOLATED;
	}

	isOppositeDirection(button) {
		return this.#buttonIndex == button.#buttonIndex && this.#direction != button.#direction;
	}
}

/**
 * GamepadManager represents the state of the complete gamebad
 */
class GamepadManager {
	gamepad;
	buttons = [];
	#userInterface;
	#mapping = "";
	#lastChangeTimestamp = 0;

	/**
	 * @param userInterface UserInterface - references to the user interface object
	 * @param mapping       string        - button mapping for ↖️⬆️↗️⬅️➡️↙️⬇️↘️YXBA
	 */
	constructor(userInterface, mapping) {
		this.#userInterface = userInterface;
		this.#mapping = mapping;
		window.addEventListener("gamepadconnected", (e) => {
			this.#onGamepadConnected(e);
		});
	}

	/**
	 * eventhandler triggered by activating the gamepad.
	 * it configures the on-screen gamepad
	 */
	#onGamepadConnected(e) {
		console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
			e.gamepad.index, e.gamepad.id,
			e.gamepad.buttons.length, e.gamepad.axes.length);
		this.gamepad = e.gamepad;
		this.#parseConfiguration();
		this.#userInterface.onGamepadReady();
	}

	/**
	 * parses the button mapping
	 */
	#parseConfiguration() {
		let entries = this.#mapping.trim().split(/[\s,]+/);
		
		for (let uiIndex = 0; uiIndex < entries.length; uiIndex++) {
			let entry = entries[uiIndex];
			if (entry === "*") {
				continue;
			}

			let direction = 0;
			if (entry.endsWith("-")) {
				direction = -1;
				entry = entry.substring(0, entry.length - 1);
			} else if (entry.endsWith("+")) {
				direction = +1;
				entry = entry.substring(0, entry.length - 1);
			}
			let buttonIndex = Number.parseInt(entry, 10);
			this.buttons.push(new GamepadButton(uiIndex, this, buttonIndex, direction));
		}
	}

	/**
	 * did the user press or release buttons since the last call to this method?
	 *
	 * @return boolean
	 */
	changesPressent() {
		if (!this.gamepad) {
			return false;
		}
		let changes = this.gamepad.timestamp > this.#lastChangeTimestamp;
		this.#lastChangeTimestamp = this.gamepad.timestamp;
		return changes;
	}

	/**
	 * checks whether the user is complying with rules
	 *
	 * @return ComplianceStatus
	 */	
	checkComplianceStatus() {
		let complianceStatus = ComplianceStatus.COMPLIANT;
		for (let button of this.buttons) {
			complianceStatus = ComplianceStatus.worst(complianceStatus, button.checkComplianceStatus());
		}
		return complianceStatus;
	}

	/**
	 * checks whether the specified button can be pressed in parallel (e. g. not the opposite on the d-pad)
	 *
	 * @param button GamepadButton - button to test
	 * @return boolean
	 */
	isButtonPossible(desiredButton) {
		for (let button of this.buttons) {
			if (button.isPressed() && button.isOppositeDirection(desiredButton)) {
				return false;
			}
		}
		return true;
	}
}


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
	}

	/**
	 * event handler
	 */
	onGamepadReady() {
		console.log(this.#gamepadManager);
		this.#showConfiguredGamepad();
		setInterval(() => {
			this.#gameloop();
		}, 1);
		this.#ruleset.start();
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
	#displayButtonState() {
		if (!this.#gamepadManager.changesPressent()) {
			return;
		}
		for (let button of this.#gamepadManager.buttons) {
			if (button.isPressed()) {
				document.getElementById("t" + button.uiIndex).classList.add("pressed");
			} else {
				document.getElementById("t" + button.uiIndex).classList.remove("pressed");
			}
		}
	}

	#gameloop() {
		this.#displayButtonState();
		if (!this.active) {
			return;
		}
		let complianceStatus = this.#gamepadManager.checkComplianceStatus();
		document.getElementById("complianceStatus").innerText = complianceStatus;
	}
}

async function init() {
	window.remoshock = new Remoshock();
	await remoshock.init();
	let appConfig = {
		immuneDuration: 3000,
		action: "BEEPSHOCK",
		receiver: 1,
		power: 30,
		duration: 500
	};
	//let ui = new UserInterface("    * 7- * 6- * 6+ * 7+ *, 3 2 1 0");
	let ui = new UserInterface(appConfig, "2 5- 1 4- * 4+ 3 5+ 0"); // select: 8, start: 9
	ui.active = true;
}

init();


