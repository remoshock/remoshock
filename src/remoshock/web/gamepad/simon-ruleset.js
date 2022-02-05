//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________

"use strict";

import { Ruleset } from "./ruleset.js";
import { ComplianceStatus } from "./gamepad.js";


/**
 * a game which order the player to press random buttons
 */
export class SimonRuleset extends Ruleset{
	#appConfig;
	#ui;
	#gamepadManager;
	#availableButtons;
	#holdButtons;
	#nextButtonPick;
	#endTime;
	#lastComplianceStatus;
	#pendingStartTime;


	constructor(appConfig, ui, gamepadManager) {
		super(appConfig, 100, ui);
		this.#appConfig = appConfig;
		this.#ui = ui;
		this.#gamepadManager = gamepadManager;
	}


	/**
	 * checks the configuration
	 */
	validateConfiguration() {
		let error = super.validateConfiguration();
		if (!this.#appConfig.play_buttons && !this.#appConfig.hold_buttons) {
			error = error + "Required setting \"buttons\" or \"hold_buttons\" are both missing.\n"
		}
		if (isNaN(parseInt(this.#appConfig.reaction_ms))) {
			error = error + "Required setting \"reaction_ms\" is missing or not a number.\n"
		}
		if (isNaN(parseInt(this.#appConfig.pick_interval_s))) {
			error = error + "Required setting \"pick_interval_s\" is missing or not a number.\n"
		}
		return error;
	}


	/**
	 * starts the game
	 */
	start() {
		let currentTime = Date.now();
		this.#endTime = currentTime + parseInt(this.#appConfig.runtime_min, 10) * 60 * 1000;
		this.#availableButtons = this.#parseButtonArray(this.#appConfig.play_buttons);
		this.#holdButtons = this.#parseButtonArray(this.#appConfig.hold_buttons);
		for (let button of this.#gamepadManager.buttons) {
			button.resetDesiredButtonStatus();
		}
		this.#pickDesiredButton(currentTime);
		this.#pendingStartTime = currentTime;
		super.start();
	}


	/**
	 * parses a string of buttons an array of numbers, skipping missing buttons
	 *
	 * @param str string to parse, may be undefined, null or empty
	 * @return array
	 */
	#parseButtonArray(str) {
		let res = [];
		if (str == undefined || str == "") {
			return res;
		}
		let configured = str.trim().split(/[\s,]+/).map(Number);
		for (let button of configured) {
			// skipt buttons, that do not exist on the current gamepad
			if (this.#gamepadManager.getButtonByUiIndex(button)) {
				res.push(button);
			}
		}
		return res;
	}


	/**
	 * If the player has violated the rules or is too slow to react, punishment will be triggered
	 *
	 * @param currentTime current time in ms
	 */
	#punishIfRequired(complianceStatus, currentTime) {
		if (complianceStatus == ComplianceStatus.VIOLATED) {
			this.punish();
		}

		if (complianceStatus == ComplianceStatus.PENDING) {
			if (this.#lastComplianceStatus !== ComplianceStatus.PENDING) {
				this.#pendingStartTime = currentTime;
			}
			let reaction_ms = parseInt(this.#appConfig.reaction_ms, 10);
			if (this.#pendingStartTime + reaction_ms < currentTime) {
				this.punish();
			}
		}
	}

	/**
	 * picks a random element from an array
	 *
	 * @param array to pick from
	 * @return random element
	 */
	randomElement(array) {
		return array[Math.floor(Math.random() * array.length)];
	}


	/**
	 * picks the desired button.
	 */
	#pickDesiredButton(currentTime) {

		// reset desired button status to false, unless it is a button,
		// that must be hold down for the entire game
		for (let button of this.#gamepadManager.buttons) {
			button.desiredButtonStatus = this.#holdButtons.indexOf(button.uiIndex) > -1;
		}

		// if there are no play buttons, this is just a game of stay.
		if (this.#availableButtons.length === 0) {
			this.#ui.displayButtonState();
			return;
		}

		let randomButton = this.randomElement(this.#availableButtons)
		this.#gamepadManager.getButtonByUiIndex(randomButton).desiredButtonStatus = true;
		this.#ui.displayButtonState();
		let offset = this.#appConfig.pick_interval_s * 1000;
		offset = offset + Math.random() * offset / 3 - offset / 6;
		this.#nextButtonPick = currentTime + offset;
	}


	/**
	 * picks a new button, if enough time has elapsed since the last pick
	 */
	#pickDesiredButtonIfItIsTime(currentTime) {
		if (this.#nextButtonPick < currentTime) {
			this.#pickDesiredButton(currentTime);
		}
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

		let complianceStatus = this.#gamepadManager.checkComplianceStatus();
		if (complianceStatus == ComplianceStatus.COMPLIANT) {
			this.#ui.displayButtonState();
		}
		let countdown = "";
		if (this.#appConfig.show_timer > 0) {
			countdown = new Date(this.#endTime - currentTime).toLocaleTimeString("de", { timeZone: 'UTC' });
		}
		this.#ui.showInformation(countdown + " " + complianceStatus);

		this.#punishIfRequired(complianceStatus, currentTime);
		this.#pickDesiredButtonIfItIsTime(currentTime);

		this.#lastComplianceStatus = complianceStatus;
	}
}

window.rulesets = window.rulesets || {}
rulesets["simon"] = SimonRuleset;
