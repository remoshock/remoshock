//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________

"use strict";

import { Ruleset } from "./ruleset.js";
import { ComplianceStatus } from "./gamepad.js";


/**
 * a game which requires the player to stay on certain buttons
 */
export class StayRuleset extends Ruleset{
	#appConfig;
	#ui;
	#gamepadManager;
	#endTime;
	#lastComplianceStatus;
	#pendingStartTime;

	constructor(appConfig, ui, gamepadManager) {
		super(appConfig, 100, ui);
		this.#appConfig = appConfig;
		this.#appConfig = appConfig;
		this.#ui = ui;
		this.#gamepadManager = gamepadManager;
	}

	/**
	 * checks the configuration
	 */
	validateConfiguration() {
		let error = super.validateConfiguration();
		if (!this.#appConfig.buttons) {
			error = error + "Required setting \"buttons\" is missing.\n"
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
		let buttons = this.#appConfig.buttons.trim().split(/[\s,]+/);
		for (let button of buttons) {
			this.#gamepadManager.getButtonByUiIndex(button).desiredButtonStatus = true;
		}
		this.#ui.displayButtonState();
		this.#endTime = Date.now() + parseInt(this.#appConfig.runtime_min, 10) * 60 * 1000;
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

		let complianceStatus = this.#gamepadManager.checkComplianceStatus();
		let countdown = new Date(this.#endTime - currentTime).toLocaleTimeString("de", { timeZone: 'UTC' });
		this.#ui.showInformation(countdown + " " + complianceStatus);

		if (complianceStatus == ComplianceStatus.VIOLATED) {
			this.punish();
		}

		if (complianceStatus == ComplianceStatus.PENDING) {
			if (complianceStatus !== this.#lastComplianceStatus) {
				this.#pendingStartTime = currentTime;
			}
			let reaction_ms = parseInt(this.#appConfig.reaction_ms, 10);
			if (this.#pendingStartTime + reaction_ms < currentTime) {
				this.punish();
			}
		}

		this.#lastComplianceStatus = complianceStatus;
	}
}

window.rulesets = window.rulesets || {}
rulesets["stay"] = StayRuleset;
