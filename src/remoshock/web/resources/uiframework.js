//
// Copyright nilswinter 2020-2022. License: AGPL
// _____________________________________________


"use strict";


export class UIFramework {

	load(data) {
		for (let key of Object.keys(data)) {
			let element = document.getElementById(key);
			if (element) {
				element.value = data[key];
			}
		}
	}

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
