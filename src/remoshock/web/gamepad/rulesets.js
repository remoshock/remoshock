//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________

"use strict";

/**
 * an abstract class for rulesets
 */
class Ruleset {
	#lastPunishmentTime = 0;
	#intervalHandle;
	#punishmentInProgress = false;
	#appConfig;

	constructor(appConfig) {
		this.#appConfig = appConfig;
	}

	/**
	 * punishes the player, but makes sure not to stack punishments
	 */
	async punish() {
		let currentTime = Date.now();
		let immune_ms = parseInt(this.#appConfig.immune_ms, 10);
		if (!this.#punishmentInProgress && this.#lastPunishmentTime + immune_ms < currentTime) {
			this.#punishmentInProgress = true
			let body = document.getElementsByTagName("body")[0];
			body.classList.add("punishing");
			await remoshock.command(
				parseInt(this.#appConfig.receiver, 10),
				this.#appConfig.action,
				parseInt(this.#appConfig.power, 10),
				parseInt(this.#appConfig.duration, 10));
			body.classList.remove("punishing");
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
		}, 100);
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


/**
 * a game which requires the player to stay on certain buttons
 */
class StayRuleset extends Ruleset{
	#appConfig;
	#ui;
	#gamepadManager;
	#endTime;
	#lastComplianceStatus;
	#pendingStartTime;

	constructor(appConfig, ui, gamepadManager) {
		super(appConfig);
		this.#appConfig = appConfig;
		this.#ui = ui;
		this.#gamepadManager = gamepadManager;
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
		document.getElementById("complianceStatus").innerText = countdown + " " + complianceStatus;

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
