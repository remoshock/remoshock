//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________
"use strict";

import "/resources/remoshock.js"
import { UIFramework } from "../resources/uiframework.js"

/**
 * a debugger
 */
class Debugger {

	constructor() {
		new UIFramework().renderAppShell("Debugger");
		document.getElementById("start").addEventListener("click", () => {
			this.#clickHandler();
		});
		this.#init();
	}

	/**
	 * init remoshock
	 */
	async #init() {
		window.remoshock = new Remoshock();
		await remoshock.init();
	}

	/**
	 * handles click events
	 */
	async #clickHandler() {
		let output = document.getElementById("output")
		for (let i = 1; i < 1000; i++) {
			for (let j = 1; j < 4; j++) {
				output.innerText = i + " . " + j;
				await remoshock.command(1, "SHOCK", 40, i, "debug");
				await remoshock.sleep(3000 + (i*10));
			}
		}
	}
}

new Debugger();
