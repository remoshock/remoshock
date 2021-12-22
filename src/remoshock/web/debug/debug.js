//
// Copyright nilswinter 2020-2021. License: AGPL
// _____________________________________________
"use strict";

import "/resources/remoshock.js"


async function clickHandler() {
	let output = document.getElementById("output")
	for (let i = 1; i < 1000; i++) {
		for (let j = 1; j < 4; j++) {
			output.innerText = i + " . " + j;
			await command(1, "SHOCK", 40, i);
			await sleep(3000 + (i*10));
		}
	}
}


async function init() {
	window.remoshock = new Remoshock();
	await remoshock.init();
	document.getElementById("start").addEventListener("click", clickHandler);
}

init();


