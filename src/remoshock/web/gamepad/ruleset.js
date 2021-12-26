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
				parseInt(this.#appConfig.power, 10),
				parseInt(this.#appConfig.duration, 10));
			this.#ui.stopIndicating("punishing");
			this.#punishmentInProgress = false
			this.#lastPunishmentTime = currentTime;
		}
	}

	/**
	 * starts compliance checks
	 */
	start() {
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
