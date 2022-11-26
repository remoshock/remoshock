"use strict";

/**
 * API wrapper for remoshock
 */
class Remoshock {
	static #COOKIE_NAME = "authentication_token";

	/**
	 * constructor
	 *
	 * @param urlprefix optional defaults to /remoshock
	 * @param token optional authentication token defaults to the cookie authentication_token 
	 */
	constructor(urlprefix, token) {
		this.urlprefix = urlprefix || "/remoshock";
		this.authenticationToken = token || this.#readAuthCookie();
	}


	/**
	 * read the authentication cookie
	 */
	#readAuthCookie() {
		let cookie = document.cookie
			.split('; ')
			.find(row => row.startsWith(Remoshock.#COOKIE_NAME + "="))
		if (!cookie) {
			return undefined;
		}
		let token = cookie.split('=')[1];
		return token;
	}


	/**
	 * replaces the webpage with an authentication form
	 */
	#authenticate() {
		document.getElementsByTagName("body")[0].innerHTML = `
			<form>
			<label for="authenticationtoken">Authentication Token:</label>
			<input id="authenticationtoken" name="authenticationtoken" autofocus type="password" required>
			<button id="loginbutton">Login</button>
			</form>
			`;
		document.getElementById("loginbutton").addEventListener("click", function(event) {
			let token = document.getElementById("authenticationtoken").value;
			document.cookie = Remoshock.#COOKIE_NAME + "=" + encodeURIComponent(token)
				+ "; path=/; max-age=" + (60*60*24*365*100) + "; samesite=lax";
			event.preventDefault();
			window.location.reload();
			return false;
		});
	}

	/**
	 * invokes a REST service via POST with an json object
	 *
	 * @param url url to post to
	 * @para data data to convert to JSON and post
	 */
	#postJson(url, data) {
		return fetch(url, {
			method: "POST",
			headers: {
				"Authorization": "Bearer " + this.authenticationToken,
				"Content-Type": "application/json"
			},
			body: JSON.stringify(data)
		});
	}

	/**
	 * reads the response from a fetch and displays a dialog on errors
	 *
	 * @param response from a fetch
	 * @return data or undefined in case of an error
	 */
	async #readResponseWithErrorPopup(response) {
		if (response.status == 500) {
			let message = await response.text();
			alert("Error returned by server: \n" + message);
			return undefined;
		} else if (response.status == 422) {
			let error = await response.json()
			alert(error.error);
		}
		return await response.json()
	}

	/**
	 * await-able sleep
	 *
	 * @param ms duration in ms
	 */
	sleep(ms) {
		return new Promise(resolve => setTimeout(resolve, ms));
	}

	/**
	 * sends a command to the server
	 *
	 * @param receiver number of receiver
	 * @param action "LIGHT", "BEEP", "VIBRATE", "SHOCK", "BEEPSHOCK"
	 * @param power  power level 0-100
	 * @param duration duration in ms
	 */
	command(receiver, action, power, duration) {
		let url = this.urlprefix + "/command"
		let command = {
			"receiver": receiver,
			"action": action,
			"power": power,
			"duration": duration
		}
		return this.#postJson(url, command);
	}

	/**
	 * saves settings to the server
	 *
	 * @param section  name of section header
	 * @param settings a map-like object
	 */
	saveSettings(section, settings) {

		// update this.config.settings
		if (!this.config["settings"][section]) {
			this.config["settings"][section] = {};
		}
		for (let key of Object.keys(settings)) {
			this.config["settings"][section][key] = settings[key];
		}

		// save to server
		let url = this.urlprefix + "/config";
		let config = {};
		config["settings"] = {};
		config["settings"][section] = settings;
		return this.#postJson(url, config);
	}

	/**
	 * starts the randomizer
	 *
	 * @param config temporary configuration
	 */
	async startRandomizer(config) {
		let url = this.urlprefix + "/randomizer/start";
		let response = await this.#postJson(url, config);
		return await this.#readResponseWithErrorPopup(response);
	}

	/**
	 * reads the randomizer status and configuration
	 *
	 * @return status and temporary config
	 */
	async readRandomizer() {
		let url = this.urlprefix + "/randomizer";
		let response = await fetch(url, {
			headers: {
				Authorization: "Bearer " + this.authenticationToken
			}
		});
		return await this.#readResponseWithErrorPopup(response);
	}

	/**
	 * stops the randomizer
	 */
	async stopRandomizer() {
		let url = this.urlprefix + "/randomizer/stop";
		let response = await this.#postJson(url, {});
		return await this.#readResponseWithErrorPopup(response);
	}


	/**
	 * initializes remoshock and download configuration from server
	 */
	async init() {
		let response = await fetch(this.urlprefix + "/config.json", {
			headers: {
				Authorization: "Bearer " + this.authenticationToken
			}
		});

		// if the server response with 403 Forbidden, ask the user for the token
		if (response.status == 403) {
			this.#authenticate();
			// this promise will never resolve because we do not want normal
			// operation to continue
			return new Promise(function() {});
		}
		this.config = await response.json()
	}
}

// explicitly export class to support ES module imports
globalThis.Remoshock = Remoshock;
