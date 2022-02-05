//
// Copyright nilswinter 2020-2022. License: AGPL
// _____________________________________________


"use strict";

/**
 * global user interface
 */
export class UIFramework {

	#appShellHTML = `<header class="appshell-header">
	<nav class="appshell-nav">
		<input type="checkbox" id="appshell-navtrigger" class="appshell-navtrigger" />
			<label for="appshell-navtrigger">
			<span class="appshell-menuicon">
				<svg viewBox="0 0 18 15" width="18px" height="15px">
					<path d="M18,1.484c0,0.82-0.665,1.484-1.484,1.484H1.484C0.665,2.969,0,2.304,0,1.484l0,0C0,0.665,0.665,0,1.484,0 h15.032C17.335,0,18,0.665,18,1.484L18,1.484z M18,7.516C18,8.335,17.335,9,16.516,9H1.484C0.665,9,0,8.335,0,7.516l0,0 c0-0.82,0.665-1.484,1.484-1.484h15.032C17.335,6.031,18,6.696,18,7.516L18,7.516z M18,13.516C18,14.335,17.335,15,16.516,15H1.484 C0.665,15,0,14.335,0,13.516l0,0c0-0.82,0.665-1.483,1.484-1.483h15.032C17.335,12.031,18,12.695,18,13.516L18,13.516z"/>
				</svg>
			</span>
		</label>

		<div class="appshell-navpopup">
			<a class="appshell-navlink" href="/remote/">Remote</a>
			<a class="appshell-navlink" href="/randomizer/">Randomizer</a>
			<a class="appshell-navlink" href="/gamepad/">Gamepad (Experimental)</a>
			<hr>
			<a class="appshell-navlink" href="https://remoshock.github.io/applications.html">Documentation</a>
		</div>
	</nav>
	<div class="appshell-title"></div>
</header>`;

	/**
	 * renders the app shell (header, footer, etc.)
	 *
	 * @param title page title as displayed in the app bard
	 */
	renderAppShell(title) {
		let header = document.getElementById("appshell-headerslot")
		if (header.childElementCount > 0) {
			return;
		}
		header.innerHTML = this.#appShellHTML;
		document.querySelector(".appshell-title").textContent = title;
	}

	/**
	 * loads data into a web page
	 *
	 * @param data a map-like object
	 */
	load(data) {
		if (!data) {
			return;
		}
		for (let key of Object.keys(data)) {
			let element = document.getElementById(key);
			if (element) {
				element.value = data[key];
				element.setCustomValidity("");
			}
		}
	}

	/**
	 * saves input fields from a webpage to a javascript object
	 *
	 * @param rootElement HTMLElement
	 * @param data map-like object to save to
	 * @return data
	 */
	save(rootElement, data) {
		let elements = rootElement.querySelectorAll("input, select")
		for (let element of elements) {
			if (element.value) {
				data[element.id] = element.value;
			}
		}
		return data;
	}
}
