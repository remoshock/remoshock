"use strict";


(function() {
	const COOKIE_NAME = "authentication_token";

	function readAuthCookie() {
		let cookie = document.cookie
			.split('; ')
			.find(row => row.startsWith(COOKIE_NAME + "="))
		if (!cookie) {
			return undefined;
		}
		let token = cookie.split('=')[1];
		return token;
	}

	function readAuthLocationHash() {
		let token = window.location.hash.substring(7);
		return token;
	}

	function createAuthCookie(token) {
		document.cookie = COOKIE_NAME + "=" + encodeURIComponent(token)
			+ "; path=/; max-age=" + (60*60*24*365*100) + "; samesite=lax";
	}

	function onLoginClick(event) {
		let token = document.getElementById("authenticationtoken").value;
		createAuthCookie(token);
		event.preventDefault();
		window.location.reload();
		return false;
	}

	function authenticate() {
		let tokenFromCookie = readAuthCookie();
		let tokenFromHash = readAuthLocationHash();

		// If there is a token in the url location hash and it is not
		// already part of the authentication_token cookie, use it
		if (tokenFromHash && tokenFromCookie !== tokenFromHash) {
			createAuthCookie(tokenFromHash);
			window.location.reload();
			return false;
		}

		// At this point there is either no token in the url location hash.
		// Or we already had a cookie with the same value. But it was not 
		// accepted by the server
		// ==> ask for token
		document.getElementsByTagName("body")[0].innerHTML = `
			<form>
			<label for="authenticationtoken">Authentication Token:</label>
			<input id="authenticationtoken" name="authenticationtoken" autofocus type="password" required>
			<button id="loginbutton">Login</button>
			</form>
			`;
		document.getElementById("loginbutton").addEventListener("click", onLoginClick);
	}

	authenticate();
})();