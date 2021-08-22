# <img src="https://raw.githubusercontent.com/remoshock/remoshock/master/src/web/favicon.png" alt="Logo showing a drawing of a shock collar receiver" height="32">&nbsp;&nbsp; remoshock

Quick links:&nbsp;&nbsp;
<a href="https://github.com/remoshock/remoshock/blob/master/docs/WARNING.md">
<img alt="Warning" src="https://img.shields.io/badge/-Warning-red"></a> 
<a href="https://github.com/remoshock/remoshock/blob/master/docs/FAQ.md">
<img alt="Frequently Asked Questions" src="https://img.shields.io/badge/-FAQ-yellow"></a> 
<a href="https://github.com/remoshock/remoshock/blob/master/docs/LICENSE.md">
<img alt="License: AGPL" src="https://img.shields.io/badge/-AGPL-%23AAF"></a> 
<a href="https://github.com/remoshock/remoshock/releases">
<img alt="Changes" src="https://img.shields.io/badge/-Changes-green"></a> 

<div>
<a href="https://raw.githubusercontent.com/remoshock/remoshock/master/docs/randomizer.png">
<img style="border: 1px #AAA solid; padding: 1em" alt="Randomizer" src="https://raw.githubusercontent.com/remoshock/remoshock/master/docs/randomizer.png" height="200"></a> 
<a href="https://raw.githubusercontent.com/remoshock/remoshock/master/docs/pac.jpeg">
<img style="border: 1px #AAA solid; padding: 1em" alt="Photo of PAC collars with HackRF SDR" src="https://raw.githubusercontent.com/remoshock/remoshock/master/docs/pac.jpeg" height="200"></a> 
<a href="https://raw.githubusercontent.com/remoshock/remoshock/master/docs/remote.png">
<img style="border: 1px #AAA solid; padding: 1em" alt="Remote Control User Interface" src="https://raw.githubusercontent.com/remoshock/remoshock/master/docs/remote.png" height="200"></a>
</div>

remoshock is a computer based remote control for shock collars.

It consists of
- a web-based user interface, that works on mobile
- a randomizer program
- a command line interface program.
- a web-based API


## ✔️ Requirements

- One or more compatible shock collars:
  - PAC collars (compatible with ATX or DTX remote)
  - Wodondog "Dog Shock Collar"
  - Petrainer
- A Software Defined Radio (SDR) transmitter that works on the required frequencies (tested using a HackRF device).
- Linux with Python 3 (tested on Ubuntu 20.04)
- Universal Radio Hacker:<br>
  `sudo apt install python3-pip python3-pyqt5; sudo pip3 install urh`
- `sudo pip3 install remoshock` 
  <br>Alternatively: Download [remoshock-0.5.zip](https://github.com/remoshock/remoshock/releases/download/v0.5/remoshock-0.5.zip) manually.
- Please see [docs/FAQ.md](https://github.com/remoshock/remoshock/blob/master/docs/FAQ.md) for troubleshooting tips.


## 🔧 Getting Started

Make sure that `urh` is working and does recognize your SDR device.

Run `remoshockcli`. This command will ask you about the number and
types of receivers in order to generate a `remoshock.ini` configuration
file. It will use random values for authentication token and transmitter
code.


Reset your collar into pairing mode and invoke `remoshockcli` again.
After successful pairing, run it a third time, to issue a "beep" command.

If you have more than one receiver, please repeat this step for each
device: `remoshock --receiver=1`, `remoshock --receiver=2`, etc.


## 🖥 Command line interface (remoshockcli)

remoshockcli allows you to send commands using the command line ("terminal window").

By default, it will send a BEEP command to the first receiver configured in `remoshock.ini`.

For example, to send a shock with 10% power for a duration of 250ms to the first receiver:

`remoshockcli --receiver 1 --action SHOCK --power 10 --duration 250`

The following actions are supported:

- **LIGHT**:  blinks the light. Note: This might cause a tiny shock on PAC collars.
- **BEEP**:   plays the beep sound
- **VIBRATE**:   Note: This will beep on collars without vibration support (e. g. PAC)
- **SHOCK**:  a shock.
- **BEEPSHOCK**: plays one beep sound, waits one second, and then triggers a shock according to parameters.

~~~~
usage: remoshockcli [-h] [-r n] [-a {LIGHT,BEEP,VIBRATE,SHOCK,BEEPSHOCK}] [-d n] [-p n] [-v] [--version]

Shock collar remote

optional arguments:
  -h, --help            show this help message and exit
  -a {LIGHT,BEEP,VIBRATE,SHOCK,BEEPSHOCK}, --action {LIGHT,BEEP,VIBRATE,SHOCK,BEEPSHOCK}
                        Action to perform
  -d n, --duration n    duration in ms (Note: PAC uses an impulse duration of 250ms)
  -p n, --power n       power level (0-100)
  -r n, --receiver n    index of receiver entry from remoshock.ini, starting at 1
  -v, --verbose         prints debug messages
  --version             show program's version number and exit

Please see https://github.com/remoshock/remoshock for documentation.
~~~~


## 📱 Interactive Remote Control (remoshockserver)

remoshockserver will start a web server, that will provide a user interface
as shown on the screenshot.

The webpage will work on mobile devices, provided that the mobile device
can reach the IP address of the computer. For example because both devices
are in the same Wifi network.

You may make the server available on the Internet, if your computer has a public
IP-address, either directly or via a VPN/tunnel. Furthermore SSH reverse port
forwarding does work. This documentation, however, will not go into detail
on how to make a server available to the Internet because of the security
implications.

`remoshockserver` will start the server and print the URL. The port and
authentication token may be configured in remoshock.ini.

~~~~
usage: remoshockserver [-h] [-v] [--version]

Shock collar remote control

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         prints debug messages
  --version             show program's version number and exit

Please see https://github.com/remoshock/remoshock for documentation.
~~~~

## 🎲 Randomizer (remoshockrnd)

remoshockrnd sends timed commands that can be randomized. For example it may
send a beep followed a shock every 5 to 15 minutes. For a completely deterministic
experience, set min and max to the same value.

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
start_delay_min_minutes=0
start_delay_max_minutes=0
runtime_min_minutes = 1440
runtime_max_minutes = 1440
~~~~

This sample configuration will ensure that there is always (100% probability)
a beep followed by a shock. The shock duration will vary between 250ms and
500ms. On a PAC collar this equals to either one or two impulses. The power
of the shocks will vary between 5% and 10%. And finally the timer will be
set to a random value between 5 minutes (300s) and 15 minutes (900s).

After the event the timer will be set to a new random value in this range and
everything will start anew. In this example remoshockrnd will end after one day
(1440 minutes) or when Ctrl+c is pressed. The runtime starts counting after
the optional initial start_delay has expired.

`remoshockrnd`

You can prepare multiple rules by using different [section]-names in remoshock.ini:

`remoshockrnd -s other_section`

~~~~
usage: remoshockrnd [-h] [-s SECTION] [-v] [--version]

Shock collar remote randomizer

optional arguments:
  -h, --help            show this help message and exit
  -s SECTION, --section SECTION
                        name of [section] in remoshock.ini to use. Default is [randomizer].
  -v, --verbose         prints debug messages
  --version             show program's version number and exit

Please see https://github.com/remoshock/remoshock for documentation.
~~~~

## 📝 remoshock.ini

The file `remoshock.ini` is automatically created with random tokens and transmitter codes
when you start remoshock for the first time.


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
channel=1
~~~~

Each receiver section has the following parameters:

- **name**: A name to display in the user interface
- **color**: A HTML color code used by the user interface
- **transmitter_code**: The transmitter bit code. You can use a random value of exactly 9 bits. Or it can be the same code as your real device. Use network bit order.
- **channel**: The button number as used by the DXT remote (top right is 1, button left is 6). In E/P-mode the left side is code 0, and the right side is code 2. Button code 7 works as well.

There may be sections for the randomizer, which are documented above.

## 🐞 Bugs and Feature Ideas

Please report bugs and feature ideas as issues on [https://github.com/remoshock/remoshock](https://github.com/remoshock/remoshock)


## 🔎 See also

- [docs/LICENSE.md](https://github.com/remoshock/remoshock/blob/master/docs/LICENSE.md)
- [docs/WARNING.md](https://github.com/remoshock/remoshock/blob/master/docs/WARNING.md)
- [docs/FAQ.md](https://github.com/remoshock/remoshock/blob/master/docs/FAQ.md)
