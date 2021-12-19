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
		if (!this.#punishmentInProgress && this.#lastPunishmentTime + this.#appConfig.immuneDuration < currentTime) {
			this.#punishmentInProgress = true
			console.log("punish", "start");
			await remoshock.command(this.#appConfig.receiver, this.#appConfig.action, this.#appConfig.power, this.#appConfig.duration);
			console.log("punish", "end");
			this.#punishmentInProgress = false
			this.#lastPunishmentTime = currentTime;
		}
	}

	/**
	 * starts compliance checks
	 */
	start() {
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
 * a game which requires the player to press certain buttons
 */
class StayRuleset extends Ruleset{
	#ui;
	#gamepadManager;

	constructor(appConfig, ui, gamepadManager) {
		super(appConfig);
		this.#ui = ui;
		this.#gamepadManager = gamepadManager;
	}

	_gameloop() {
		if (!this.#ui.active) {
			return;
		}
		let complianceStatus = this.#gamepadManager.checkComplianceStatus();
		document.getElementById("complianceStatus").innerText = complianceStatus;

		if (complianceStatus == ComplianceStatus.VIOLATED) {
			this.punish();
		}

		// TODO: PENDING for too long
	}
}
