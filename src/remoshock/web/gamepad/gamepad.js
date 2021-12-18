"use strict";

/**
 * a gamepad button. This class handles both real buttons, and axis-based directional buttons.
 */
class GamepadButton {
	uiIndex = -1;
	#direction = 0;
	#gamepadRef = undefined;

	/**
	 * @param index          number - of the userinterface representation
	 * @param gamepadManager GamepadManager - reference to the gamepad
	 * @param buttonIndex    number - index as used by the Web GamepadAPI
	 * @param direction      number - 0 for buttons, -1 or 1 for directional buttons
	 */
	constructor(uiIndex, gamepadManager, buttonIndex, direction) {
		this.uiIndex = uiIndex;
		this.#direction = direction;
		if (direction === 0) {
			this.#gamepadRef = gamepadManager.gamepad.buttons[buttonIndex];
		} else {
			// TODO: this approach does not work because
			//       axes are not objects but simple values
			this.#gamepadRef = gamepadManager.gamepad.axes[buttonIndex];
		}
	}

}

/**
 * GamepadManager represents the state of the complete gamebad
 */
class GamepadManager {
	#userInterface;
	#configuration = "";
	buttons = [];

	/**
	 * @param userInterface UserInterface - references to the user interface object
	 * @param configuration string        - button mapping for ↖️⬆️↗️⬅️➡️↙️⬇️↘️YXBA
	 */
	constructor(userInterface, configuration) {
		this.#userInterface = userInterface;
		this.#configuration = configuration;
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
		let entries = this.#configuration.trim().split(/[\s,]+/);
		
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
}


/**
 * user interface
 */
class UserInterface {
	#MAX_BUTTONS = 12;
	#gamepadManager;

	/**
	 * @param configuration string - button mapping for ↖️⬆️↗️⬅️➡️↙️⬇️↘️YXBA
	 */
	constructor(configuration) {
		this.#gamepadManager = new GamepadManager(this, configuration);
	}

	/**
	 * event handler
	 */
	onGamepadReady() {
		console.log(this.#gamepadManager);
		this.#showConfiguredGamepad();
	}

	/**
	 * configures the gamepad on screen by hiding missing buttons
	 */
	#showConfiguredGamepad() {
		for (let i = 0; i < this.#MAX_BUTTONS; i++) {
			document.getElementById("b" + i).classList.add("hidden");
		}
		console.log("gui", this.#gamepadManager.buttons);
		for (let button of this.#gamepadManager.buttons) {
			console.log(button);
			document.getElementById("b" + button.uiIndex).classList.remove("hidden");
		}
	}
}

let ui = new UserInterface("    * 7- * 6- 6+ * 7+ *, 3 2 1 0");
