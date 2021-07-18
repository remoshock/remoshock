# Pyshock

<div style="float: right">
<img style="border: 1px #AAA solid; margin-left: 2em; margin-right: 0.2em" alt="Remote" src="doc/remote.png" width="200">
</div>

## About the project

Pyshock is a computer based remote control for shock collars. It supports
a user interface, a web-based API and command line interface.


## Requirements

- One or more PAC shock collars (Pacdog ACX or BCX collar or anything compatible with ATX or DTX remote).
- A Software Defined Radio (SDR) transmitter such as HackRF.
- Linux with Python 3 (tested on Ubuntu 20.04)
- Universal Radio Hacker (`pip3 install urh`).


## Getting Started

Make sure that `urh` is working and does recognize your SDR device.

Reset your collar and invoke the following command:

TODO urh-cli command to send a beep. 


Create a file called `config.py` and configure your devices. Please make 
sure that the syntax is correct because this file will be read as
Python code:

~~~~
from pacdog import Pacdog

devices = [
	Pacdog(name="PAC_1", code="#FFD", code="101011001", button=1),
	Pacdog(name="PAC_2", code="#FEE", code="101011001", button=2),
	Pacdog(name="PAC_3", code="#FFD", code="101011001", button=3),
	Pacdog(name="PAC_4", code="#FEE", code="101011001", button=4),
	Pacdog(name="PAC_5", code="#FFD", code="101011001", button=5),
	Pacdog(name="PAC_6", code="#FEE", code="101011001", button=6)
];

web_authentication_token = "soizEeWyOKZt2wJz7NUn"
~~~~

Each device has the following parameters:

| Parameter |  Description |
| --------- + ------------ |
| name      | A name to display in the user interface |
| color     | A HTML color code used by the user interface |
| code      | The transmitter bit code. You can use a random value or the code of your real device |
| button    | The button number as used by the DXT remote (top right is 1, button left is 6). In E/P-mode the left side is code 0, and the right side is code 2               | 


Use a random value for `web_authentication_token` and keep it secret.

<!--


### Command line interface (pyshock-server)

TODO: code this

## Programs

### Interactive Remote Control (pyshock-cli)

TODO: documemt this

### Random (pyshock-random)

TODO: code this

## Developer documentation

### REST API documention

TODO: API documentation

-->

## See also

- [doc/LICENSE.md](doc/LICENSE.md)
- [doc/WARNING.md](doc/WARNING.md)