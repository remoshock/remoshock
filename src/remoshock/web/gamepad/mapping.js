//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________

"use strict";

import { UIFramework } from "../resources/uiframework.js"
import "/resources/remoshock.js"


class GamepadState {
	axes = [];
	buttons = [];

	constructor(gamepad) {
		for (let value of gamepad.axes) {
			if (value > 0.5) {
				this.axes.push(1);
			} else if (value < -0.5) {
				this.axes.push(-1);
			} else {
				this.axes.push(0);
			}
		}
		for (let button of gamepad.buttons) {
			this.buttons.push(button.pressed);
		}
	}
}

class GamepadStateUtil {
	
	static newlyPressed(oldGamepadState, newGamepadState) {
		let change = undefined;

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

class Mapping {

	SUPPORTED_BUTTONS = [1, 3, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16];
	#uiFramework;
	#lastGamepadState;
	#lastTimestamp = 0;
	#mapping = ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"];
	#index = 0;

	constructor() {
		this.#uiFramework = new UIFramework();
		this.#uiFramework.renderAppShell("Gamepad Mapping");
		document.getElementById("save").addEventListener("click", () => {
			this.#onSave();
		});
		document.getElementById("skip").addEventListener("click", () => {
			this.#onSkip();
		});
		document.getElementById("reload").addEventListener("click", () => {
			window.location.reload();
		});
		this.init();
	}

	async init() {
		globalThis.remoshock = new Remoshock();
		window.addEventListener("gamepadconnected", (e) => {
			this.#onGamepadConnected(e);
		});
		window.addEventListener("gamepaddisconnected", (e) => {
			window.location.reload();
		});
		await remoshock.init();
	}

	/**
	 * eventhandler triggered by activating the gamepad.
	 * it configures the on-screen gamepad
	 */
	#onGamepadConnected(e) {
		console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
			e.gamepad.index, e.gamepad.id,
			e.gamepad.buttons.length, e.gamepad.axes.length);
		this.#lastGamepadState = new GamepadState(e.gamepad);
		requestAnimationFrame(() => {
			this.#onAnimationFrame();
		});

		document.getElementById("skip").classList.remove("hidden");
		document.getElementById("reload").classList.remove("hidden");
		document.getElementById("save").classList.add("hidden");

		document.getElementById("instruction").textContent = "Gamepad detected. Please press the indicated button on your camepad or click \"Skip this button\", if it does not exist.";
		this.#index = 0;
		this.#displayButtonState();
	}

	#onAnimationFrame() {
		let gamepad = navigator.getGamepads()[0];
		if (gamepad.timestamp > this.#lastTimestamp) {

			let gamepadState = new GamepadState(gamepad);
			let code = GamepadStateUtil.newlyPressed(this.#lastGamepadState, gamepadState);
			if (code) {
				this.#advance(code);
			}

			this.#lastGamepadState = gamepadState;
			this.#lastTimestamp = gamepad.timestamp;
		}

		requestAnimationFrame(() => {
			this.#onAnimationFrame();
		});
	}

	#advance(code) {
		if (this.#index < this.SUPPORTED_BUTTONS.length) {
			this.#mapping[this.SUPPORTED_BUTTONS[this.#index]] = code;
			this.#index++;
			this.#displayButtonState();
			if (this.#index >= this.SUPPORTED_BUTTONS.length) {
				document.getElementById("save").classList.remove("hidden");
				document.getElementById("skip").classList.add("hidden");
			}
			document.getElementById("instruction").textContent = "Configuration completed. You may save it.";
		}
	}

	/**
	 * indicates the button state on the user interface
	 */
	#displayButtonState() {
		for (let i = 0; i < this.SUPPORTED_BUTTONS.length; i++) {
			let button = this.SUPPORTED_BUTTONS[i];
			if (i == this.#index) {
				document.getElementById("b" + button).classList.add("desired");
			} else {
				document.getElementById("b" + button).classList.remove("desired");
			}
		}
	}

	#onSkip() {
		this.#advance("*");
	}

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

new Mapping();