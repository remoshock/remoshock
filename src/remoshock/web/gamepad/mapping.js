//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________

"use strict";

import { UIFramework } from "../resources/uiframework.js"
import "/resources/remoshock.js"


/**
 * a gamepad state, recording pressed buttons and axes
 */
class GamepadState {
	axes = [];
	buttons = [];

	/**
	 * saves the current state of the gamepad
	 *
	 * @param gamepad optional reference to the gamepad to save
	 */
	constructor(gamepad) {
		if (!gamepad) {
			return;
		}
		for (let value of gamepad.axes) {
			if (value > 0.8) {
				this.axes.push(1);
			} else if (value < -0.8) {
				this.axes.push(-1);
			} else {
				this.axes.push(0);
			}
		}
		for (let button of gamepad.buttons) {
			this.buttons.push(button.pressed);
		}
	}

	/**
	 * extracts direction of a button code
	 *
	 * @param code button code
	 * @return -1: negative axis, 0: button, 1: positive axis
	 */
	#extractSignFromCode(code) {
		let suffix = code.charAt(code.length - 1);
		if (suffix === "+") {
			return 1;
		} else if (suffix === "-") {
			return -1;
		}
		return 0;
	}

	/**
	 * checks whether a button is pressed
	 *
	 * @param code button code
	 * @return true, if the button is pressed
	 */
	isPressed(code) {
		let sign = this.#extractSignFromCode(code);
		if (sign === 0) {
			return this.buttons[parseInt(code, 10)];
		}

		let index = parseInt(code.substring(0, code.length - 1), 10);
		let value = this.axes[index];
		return value === sign;
	}
}


/**
 * utility class to process GamepadState
 */
class GamepadStateUtil {

	/**
	 * which button has been pressed between two gamepad states.
	 *
	 * @param oldGamepadState the gamepad state before the button (axis) was pressed
	 * @param newGamepadState the gamepad state after a button (axis) was pressed
	 * @return button (axis) code of the newly pressed button, 
	 *         undefined if no or more than one button were pressed 
	 */
	static newlyPressed(oldGamepadState, newGamepadState) {
		let change = undefined;

		// check buttons
		for (let i = 0; i < newGamepadState.buttons.length; i++) {
			let newValue = newGamepadState.buttons[i];
			if (!newValue) {
				continue;
			}
			let oldValue = oldGamepadState.buttons[i];
			if (oldValue != newValue) {
				if (change) {
					console.log("found more than one button change");
					return undefined;
				}
				change = "" + i;
			}
		}

		// check axes
		for (let i = 0; i < newGamepadState.axes.length; i++) {
			let newValue = newGamepadState.axes[i];
			if (!newValue) {
				continue;
			}
			let oldValue = oldGamepadState.axes[i];
			if (oldValue != newValue) {
				if (change) {
					console.log("found more than one button change");
					return undefined;
				}
				change = "" + i;
				if (newValue < 0) {
					change = change + "-";
				} else {
					change = change + "+";
				}
			}
		}

		return change;
	}
}


/**
 * a settings page to configure gamepad mapping
 */
class Mapping {

	// for now ignore upper/left, upper/right, lower/left and lower/right buttons
	SUPPORTED_BUTTONS = [1, 3, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16];
	#uiFramework;
	state;
	#mapping = ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"];
	#index = 0;

	constructor() {
		// render the app shell
		this.#uiFramework = new UIFramework();
		this.#uiFramework.renderAppShell("Gamepad Mapping");

		// register event listeners
		window.addEventListener("gamepadconnected", (e) => {
			this.#onGamepadConnected(e);
		});
		window.addEventListener("gamepaddisconnected", () => {
			window.location.reload();
		});
		document.getElementById("save").addEventListener("click", () => {
			this.#onSave();
		});
		document.getElementById("skip").addEventListener("click", () => {
			this.#onSkip();
		});
		document.getElementById("reload").addEventListener("click", () => {
			window.location.reload();
		});

		// init remoshock, which we will need later to save the settings
		this.init();
	}

	/**
	 * initializes remoshock
	 */
	async init() {
		globalThis.remoshock = new Remoshock();
		await remoshock.init();
	}

	/**
	 * eventhandler, triggered by activating the gamepad.
	 */
	#onGamepadConnected(e) {
		console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
			e.gamepad.index, e.gamepad.id,
			e.gamepad.buttons.length, e.gamepad.axes.length);

		document.getElementById("skip").classList.remove("hidden");
		document.getElementById("reload").classList.remove("hidden");
		document.getElementById("save").classList.add("hidden");

		document.getElementById("instruction").textContent = "Gamepad detected. Please press the indicated button on your camepad or click \"Skip this button\", if it does not exist.";

		// delay initialisation of wizward to ignore the initial button press
		setTimeout(() => {
			this.#index = 0;
			this.displayButtonState(true);
			this.state = new WaitForButtonPress(this);
			requestAnimationFrame(() => {
				this.#onAnimationFrame();
			});
		}, 200);
	}

	/**
	 * read and handle gamepad state
	 */
	#onAnimationFrame() {
		this.state.onAnimationFrame();
		requestAnimationFrame(() => {
			this.#onAnimationFrame();
		});
	}

	/**
	 * advance the wizard to the next button and store the last one.
	 */
	advance(code) {
		this.state = new WaitForButtonPress(this);
		if (this.#index < this.SUPPORTED_BUTTONS.length) {
			this.#mapping[this.SUPPORTED_BUTTONS[this.#index]] = code;
			this.#index++;
			this.displayButtonState(true);

			// we are done
			if (this.#index >= this.SUPPORTED_BUTTONS.length) {
				document.getElementById("save").classList.remove("hidden");
				document.getElementById("skip").classList.add("hidden");
				document.getElementById("instruction").textContent = "Configuration completed. You may save it.";
			}
		}
	}

	/**
	 * indicates the button state on the user interface
	 *
	 * @param highlightDesired
	 */
	displayButtonState(highlightDesired) {
		for (let i = 0; i < this.SUPPORTED_BUTTONS.length; i++) {
			let button = this.SUPPORTED_BUTTONS[i];
			if (highlightDesired && (i == this.#index)) {
				document.getElementById("b" + button).classList.add("desired");
			} else {
				document.getElementById("b" + button).classList.remove("desired");
			}
		}
		// TODO: indicate pressed buttons to allow players to test their mappings
	}

	/**
	 * this button does not exist on the gamepad
	 */
	#onSkip() {
		this.advance("*");
	}

	/**
	 * save the settings using a unified browser name and gamepad name as key
	 */
	async #onSave() {
		let gamepad = navigator.getGamepads()[0];
		let key = navigator.userAgent.replaceAll(/[^A-Za-z]/g, "")
			+ "." + gamepad.id.replaceAll(/[^A-Za-z0-9]/g, "");
		let settings = {}
		settings[key.toLowerCase()] = this.#mapping.join(" ");
		await remoshock.saveSettings("gamepad-mapping", settings);
		window.location = "/gamepad/";
	}
}


/**
 * interface for the state of the wizard
 */
class State {
	onAnimationFrame() {};
}

/**
 * wizard is waiting for the user to press a button
 */
class WaitForButtonPress extends State {
	#mapping;
	#lastGamepadState;
	#lastTimestamp = 0;

	constructor(mapping) {
		super();
		this.#mapping = mapping;
		let gamepad = navigator.getGamepads()[0];
		this.#lastGamepadState = new GamepadState(gamepad);
		this.#lastTimestamp = gamepad.timestamp;
	}

	onAnimationFrame() {
		let gamepad = navigator.getGamepads()[0];
		if (gamepad.timestamp <= this.#lastTimestamp) {
			return;
		}

		// check whether a button has been pressed since we last checked	
		let gamepadState = new GamepadState(gamepad);
		let code = GamepadStateUtil.newlyPressed(this.#lastGamepadState, gamepadState);
		if (code) {
			this.#preAdvance(code);
		}
	
		this.#lastGamepadState = gamepadState;
		this.#lastTimestamp = gamepad.timestamp;
	}

	/**
	 * remebers the pressed button and waits for the user to release it
	 *
	 * @code button code 
	 */
	#preAdvance(code) {
		this.#mapping.displayButtonState(false);
		this.#mapping.state = new WaitForButtonRelease(this.#mapping, code);
	}	
}


/**
 * wait for the user to release a button
 */
class WaitForButtonRelease extends State {
	#done = false;
	#mapping;
	#code;
	#lastTimestamp = 0;

	constructor(mapping, code) {
		super();
		this.#mapping = mapping;
		this.#code = code;
	}

	onAnimationFrame() {
		if (this.#done) {
			return;
		}
		let gamepad = navigator.getGamepads()[0];
		if (gamepad.timestamp <= this.#lastTimestamp) {
			return;
		}

		// when the button was released, wait a little to work around
		// a bug in Firefox: The LT and RT axes start at 0, go up to
		// 1 when pressed, but return to -1 after release.
		// Without this delay, we see the -1 as a new button press.	
		let gamepadState = new GamepadState(gamepad);
		if (!gamepadState.isPressed(this.#code)) {
			this.#done = true;
			setTimeout(() => this.#onTimeout(), 100);
		}
	}

	#onTimeout() {
		this.#mapping.advance(this.#code);
	}
}


new Mapping();
