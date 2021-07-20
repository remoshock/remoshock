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
- Universal Radio Hacker (`apt install python3-pip; pip3 install urh`).


## Getting Started

Make sure that `urh` is working and does recognize your SDR device.

Run `pyshockcli` (when installed) or `./pyshockcli.py` (from the src folder of the source code).

This command will generate a `pyshock.ini` configuration file.
Please edit this file to specify your SDR transmitting hardware.

Reset your collar and invoke `pyshockcli` again. The collar should now be paired.
Run it a third time, to issue a "beep" command.

## pyshock.ini

Each receiver has the following parameters:

| Parameter |  Description |
| --------- + ------------ |
| name      | A name to display in the user interface |
| color     | A HTML color code used by the user interface |
| code      | The transmitter bit code. You can use a random value or the code of your real device |
| button    | The button number as used by the DXT remote (top right is 1, button left is 6). In E/P-mode the left side is code 0, and the right side is code 2               | 

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
