# Pyshock

<a href="https://github.com/pyshock/pyshock/blob/master/doc/LICENSE.md"> 
<img alt="License: AGPL" src="https://img.shields.io/badge/License-AGPL-%23AAF"></a> 
<a href="https://github.com/pyshock/pyshock/releases/download/v0.1/pyshock-0.1.zip">
<img alt="Download" src="https://img.shields.io/badge/Download-0.1-%23AFA"></a>

<div>
<a href="https://raw.githubusercontent.com/pyshock/pyshock/master/doc/randomizer.png">
<img style="border: 1px #AAA solid; padding: 1em" alt="Randomizer" src="https://raw.githubusercontent.com/pyshock/pyshock/master/doc/randomizer.png" height="200"></a> 
<a href="https://raw.githubusercontent.com/pyshock/pyshock/master/doc/pac.jpeg">
<img style="border: 1px #AAA solid; padding: 1em" alt="Photo of PAC collars with HackRF SDR" src="https://raw.githubusercontent.com/pyshock/pyshock/master/doc/pac.jpeg" height="200"></a> 
<a href="https://raw.githubusercontent.com/pyshock/pyshock/master/doc/remote.png">
<img style="border: 1px #AAA solid; padding: 1em" alt="Remote Control User Interface" src="https://raw.githubusercontent.com/pyshock/pyshock/master/doc/remote.png" height="200"></a>
</div>

Pyshock is a computer based remote control for shock collars.

It consists of
- a web-based user interface, that works on mobile
- a randomizer program
- a command line interface program.
- a web-based API


## ✔️ Requirements

- One or more PAC shock collars (Pacdog ACX or BCX collar or anything compatible with ATX or DTX remote).
- A Software Defined Radio (SDR) transmitter that works on the required frequencies (tested using a HackRF device).
- Linux with Python 3 (tested on Ubuntu 20.04)
- Universal Radio Hacker (`apt install python3-pip; pip3 install urh`).
- Download and unzip [https://github.com/pyshock/pyshock/releases/download/v0.1/pyshock-0.1.zip](https://github.com/pyshock/pyshock/releases/download/v0.1/pyshock-0.1.zip).


## 🔧 Getting Started

Make sure that `urh` is working and does recognize your SDR device.

Run `./pyshockcli.py`. This command will generate a `pyshock.ini` configuration file
with random values for authentication token and transmitter code.
Please edit this file to specify your SDR transmitting hardware.

Reset your collar into pairing mode and invoke `./pyshockcli` again.
After successful pairing, run it a third time, to issue a "beep" command.


## 🖥 Command line interface (pyshockcli)

pyshockcli allows you to send commands using the command line ("terminal window").

By default, it will send a BEEP command to the first receiver configured in `pyshock.ini`.

For example, to send a shock with 10% power for a duration of 250ms duration to the first receiver:

`./pyshockcli.py --receiver 1 --action SHOCK --power 10 --duration 250`

The following actions are supported:

- **LIGHT**:  blinks the light. Note: This might cause a tiny shock on PAC collars.
- **BEEP**:   plays the beep sound
- **VIBRATE**:   reserved for future use. Note: This will beep on PAC collars.
- **SHOCK**:  a shock.
- **BEEPSHOCK**: plays one beep sound, waits one second, and then triggers a shock according to parameters.

~~~~
usage: pyshockcli.py [-h] [-r n] [-a {LIGHT,BEEP,VIBRATE,SHOCK,BEEPSHOCK}] [-d n] [-p n] [-v] [--version]

Shock collar remote

optional arguments:
  -h, --help            show this help message and exit
  -a {LIGHT,BEEP,VIBRATE,SHOCK,BEEPSHOCK}, --action {LIGHT,BEEP,VIBRATE,SHOCK,BEEPSHOCK}
                        Action to perform
  -d n, --duration n    duration in ms (Note: PAC uses an impulse duration of 250ms)
  -p n, --power n       power level (0-100)
  -r n, --receiver n    index of receiver entry from pyshock.ini, starting at 1
  -v, --verbose         prints debug messages
  --version             show program's version number and exit

Please see https://github.com/pyshock/pyshock for documentation.
~~~~


## 📱 Interactive Remote Control (pyshockserver)

pyshockserver will start a web server, that will provide a user interface
as shown on the screenshot.

The webpage will work on mobile devices, provided that the mobile device
can reach the IP address of the computer. For example because both devices
are in the same Wifi network.

You may make the server available on the Internet, if your computer has a public
IP-address, either directly or via a VPN/tunnel. Furthermore SSH reverse port
forwarding does work. This documentation, however, will not go into detail
on how to make a server available to the Internet because of the security
implications.

`./pyshockserver.py` will start the server and print the URL. The port and
authentication token may be configured in pyshock.ini.

~~~~
usage: pyshockserver.py [-h] [-v] [--version]

Shock collar remote control

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         prints debug messages
  --version             show program's version number and exit

Please see https://github.com/pyshock/pyshock for documentation.
~~~~

## 🎲 Randomizer (pyshockrnd)

pyshockrnd sends timed commands that can be randomized. For example it may
send a beep followed a shock every 5 to 15 minutes. For a completely deterministic
experiences, set min and max to the same value.

Example configuration section:

~~~~
[randomizer]
beep_probability_percent = 100
shock_probability_percent = 100
shock_min_duration_ms = 250
shock_max_duration_ms = 500
shock_min_power_percent = 5
shock_max_power_percent = 10
pause_min_s = 300
pause_max_s = 900
max_runtime_minutes = 1440
~~~~

This sample configuration will ensure that there is always (100% probability)
a beep followed by a shock. The shock duration will vary between 250ms and
500ms. On a PAC collar this equals to either one or two impulses. The power
of the shocks will vary between 5% and 10%. And finally the timer will be
set to a random value between 5 minutes (300s) and 15 minutes (900s).

After the event the timer will be set to a new random value in this range and
everything will start anew. In this example pyshockrnd will end after one day
(1440 minutes) or when ctrl+c is pressed.

`./pyshockrnd.py`

You can prepare multiple rules by using different [section]-names in pyshock.ini:

`./pyshockrnd.py -s other_section`

~~~~
usage: pyshockrnd.py [-h] [-s SECTION] [-v] [--version]

Shock collar remote randomizer

optional arguments:
  -h, --help            show this help message and exit
  -s SECTION, --section SECTION
                        name of [section] in pyshock.ini to use. Default is [randomizer].
  -v, --verbose         prints debug messages
  --version             show program's version number and exit

Please see https://github.com/pyshock/pyshock for documentation.
~~~~

## 📝 pyshock.ini

The file `pyshock.ini` is automatically created with random tokens and transmitter codes
when you start pyshock for the first time.


~~~~
[global]
web_port = 7777    
web_authentication_token = [random unguessable value]

# URH supports the following hardware, that can transmit on 27.195 MHz (upper/lower case is important): 
# HackRF, LimeSDR

# sdr=HackRF
~~~~

The [global] contains general settings. `web_port` and `web_authentication_token`
are used by the web-based remote control user interface.

Please configure the name of your SDR transmitter in the configuration
setting `sdr` (without the leading # in the above example).

~~~~
[receiver]
type=pac
name=PAC1
color=#FFD
transmitter_code=[random 9 bit value]
button=1
~~~~

Each receiver section has the following parameters:

- **name**: A name to display in the user interface
- **color**: A HTML color code used by the user interface
- **transmitter_code**: The transmitter bit code. You can use a random value of exactly 9 bits. Or it can be the same code as your real device. Use network bit order.
- **button**: The button number as used by the DXT remote (top right is 1, button left is 6). In E/P-mode the left side is code 0, and the right side is code 2. Button code 7 works as well.

There may be sections for the randomizer, which are documented above.

## 🐞 Bugs and Feature Ideas

Please report bugs and feature ideas as issues on [https://github.com/pyshock/pyshock](https://github.com/pyshock/pyshock)


## 🔎 See also

- [doc/LICENSE.md](https://github.com/pyshock/pyshock/blob/master/doc/LICENSE.md)
- [doc/WARNING.md](https://github.com/pyshock/pyshock/blob/master/doc/WARNING.md)
- [doc/FAQ.md](https://github.com/pyshock/pyshock/blob/master/doc/FAQ.md)
