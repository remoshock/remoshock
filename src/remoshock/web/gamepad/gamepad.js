//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________
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

	resetDesiredButtonStatus() {
		this.#lastButtonStatus = false;
		this.desiredButtonStatus = false;
	}
}

/**
 * GamepadManager represents the state of the complete gamebad
 */
class GamepadManager {
	gamepad;
	buttons = [];
	#userInterface;
	#uiIndexMap = {};
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
		this.#parseButtonMapping();
		this.#userInterface.onGamepadReady();
	}

	/**
	 * parses the button mapping
	 */
	#parseButtonMapping() {
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
			let button = new GamepadButton(uiIndex, this, buttonIndex, direction);
			this.buttons.push(button);
			this.#uiIndexMap[uiIndex] = button;
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
			if (button.desiredButtonStatus && button.isOppositeDirection(desiredButton)) {
				return false;
			}
		}
		return true;
	}

	/**
	 * returns a button based on its uiIndex
	 *
	 * @param uiIndex
	 * @return button
	 */
	getButtonByUiIndex(index) {
		return this.#uiIndexMap[index];
	}
}

