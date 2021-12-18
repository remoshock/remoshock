"use strict";

class GamepadButton {
	#uiIndex = -1;
	#direction = 0;
	#gamepadRef = undefined;

	constructor(uiIndex, gamepad, buttonIndex, direction) {
		this.#uiIndex = uiIndex;
		this.#direction = direction;
		if (direction === 0) {
			this.#gamepadRef = gamepad.buttons[buttonIndex];
		} else {
			this.#gamepadRef = gamepad.axis[buttonIndex];
		}
	}

}