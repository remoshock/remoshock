//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________

"use strict";

import { Ruleset } from "./ruleset.js";


/**
 * a game which requires the player to stay on certain buttons
 */
export class WalkRuleset extends Ruleset{
	#appConfig;
	#ui;
	#gamepadManager;
	#endTime;
	#buttons
	#lastPressCounts

	constructor(appConfig, ui, gamepadManager) {
		let reaction_ms = parseInt(appConfig.reaction_ms, 10);
		super(appConfig, reaction_ms, ui);
		this.#appConfig = appConfig;
		this.#ui = ui;
		this.#gamepadManager = gamepadManager;
	}


	/**
	 * checks the configuration
	 */
	validateConfiguration() {
		let error = super.validateConfiguration();
		if (!this.#appConfig.play_buttons) {
			error = error + "Required setting \"play_buttons\" is missing.\n"
		}
		if (isNaN(parseInt(this.#appConfig.reaction_ms))) {
			error = error + "Required setting \"reaction_ms\" is missing or not a number.\n"
		}
		return error;
	}


	/**
	 * starts the game
	 */
	start() {
		for (let button of this.#gamepadManager.buttons) {
			button.resetDesiredButtonStatus();
		}

		this.#buttons = [];
		this.#lastPressCounts = [];
		let buttons = this.#appConfig.play_buttons.trim().split(/[\s,]+/);
		for (let buttonUiIndex of buttons) {
			let button = this.#gamepadManager.getButtonByUiIndex(buttonUiIndex)
			button.desiredButtonStatus = true;
			this.#buttons.push(button);
			this.#lastPressCounts.push(Number.MIN_SAFE_INTEGER);
		}

		this.#endTime = Date.now() + parseInt(this.#appConfig.runtime_min, 10) * 60 * 1000;
		this.#ui.displayButtonState();
		super.start();
		
	}


	/**
	 * game logic
	 */
	_gameloop() {
		let currentTime = Date.now();
		if (currentTime > this.#endTime) {
			this.#ui.stop();
			return;
		}

		let countdown = new Date(this.#endTime - currentTime).toLocaleTimeString("de", { timeZone: 'UTC' });
		this.#ui.showInformation(countdown);

		let compliant = true;
		let temp = "";
		for (let i = 0; i < this.#buttons.length; i++) {
			let currentCount = this.#buttons[i].pressCounter;
			temp = temp + (currentCount - this.#lastPressCounts[i]) + "\t";
			if (currentCount - this.#lastPressCounts[i] < 1) {
				compliant = false;
			}
			this.#lastPressCounts[i] = currentCount;
		}
		console.log(temp);

		if (!compliant) {
			this.punish();
		}

	}
}

window.rulesets = window.rulesets || {}
rulesets["walk"] = WalkRuleset;
