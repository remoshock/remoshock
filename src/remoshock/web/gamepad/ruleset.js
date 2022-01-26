//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________

"use strict";

/**
 * an abstract class for rulesets
 */
export class Ruleset {
	#appConfig;
	#gameloopPauseTime
	#ui
	#lastPunishmentTime = 0;
	#intervalHandle;
	#punishmentInProgress = false;

	constructor(appConfig, gameloopPauseTime, ui) {
		this.#appConfig = appConfig;
		this.#gameloopPauseTime = gameloopPauseTime;
		this.#ui = ui;
	}

	/**
	 * checks the configuration
	 */
	validateConfiguration() {
		let error = "";
		if (isNaN(parseInt(this.#appConfig.immune_ms))) {
			error = error + "Required setting \"immune_ms\" is missing or not a number.\n"
		}
		if (isNaN(parseInt(this.#appConfig.receiver))) {
			error = error + "Required setting \"receiver\" is missing or not a number.\n"
		}
		let actions = ["LIGHT", "BEEP", "VIBRATE", "SHOCK", "BEEPSHOCK"];
		if (!actions.includes(this.#appConfig.action)) {
			error = error + "Required setting \"action\" is missing or not one of LIGHT, BEEP, VIBRATE, SHOCK, BEEPSHOCK.\n"
		}
		if (isNaN(parseInt(this.#appConfig.shock_power_percent))) {
			error = error + "Required setting \"shock_power_percent\" is missing or not a number.\n"
		}
		if (isNaN(parseInt(this.#appConfig.duration_ms))) {
			error = error + "Required setting \"duration_ms\" is missing or not a number.\n"
		}
		if (isNaN(parseInt(this.#appConfig.runtime_min))) {
			error = error + "Required setting \"runtime_min\" is missing or not a number.\n"
		}
		return error;
	}

	/**
	 * punishes the player, but makes sure not to stack punishments
	 */
	async punish() {
		let currentTime = Date.now();
		let immune_ms = parseInt(this.#appConfig.immune_ms, 10);
		if (!this.#punishmentInProgress && this.#lastPunishmentTime + immune_ms < currentTime) {
			this.#punishmentInProgress = true
			this.#ui.indicate("punishing");
			await remoshock.command(
				parseInt(this.#appConfig.receiver, 10),
				this.#appConfig.action,
				parseInt(this.#appConfig.shock_power_percent, 10),
				parseInt(this.#appConfig.duration_ms, 10));
			this.#ui.stopIndicating("punishing");
			this.#punishmentInProgress = false
			this.#lastPunishmentTime = currentTime;
		}
	}

	/**
	 * starts compliance checks
	 */
	start() {
		let error = this.validateConfiguration();
		if (error != "") {
			alert(error);
		}
		this.#lastPunishmentTime = Date.now();
		this.#intervalHandle = setInterval(() => {
			this._gameloop();
		}, this.#gameloopPauseTime);
	}

	/**
	 * stops compliance checks
	 */
	stop() {
		if (this.#intervalHandle) {
			clearInterval(this.#intervalHandle)
			this.#intervalHandle = undefined;
		}
	}

	/**
	 * the game loop which checks for compliance
	 */
	_gameloop() {
		// overwrite in subclass
	}

}
