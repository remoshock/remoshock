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
	            + "?receiver=" + escape(receiver)
	            + "&action=" + escape(action)
	            + "&power=" + escape(power)
	            + "&duration=" + escape(duration);
		return fetch(url, {
			headers: {
				Authorization: "Bearer " + this.authenticationToken
			},
			method: "POST"
		});
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
