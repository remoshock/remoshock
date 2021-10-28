# Frequently asked Questions and answers

## ⚠️ Risks

**Is playing with electricity dangerous?**

Yes, it is. Please see [WARNING](https://github.com/remoshock/remoshock/blob/master/docs/WARNING.md)


**Should I play with electricity?**

No, you should not. Please see [WARNING](https://github.com/remoshock/remoshock/blob/master/docs/WARNING.md)



## 🔧 About the project

**Where can I find documentation and source code?**

[https://github.com/remoshock/remoshock](https://github.com/remoshock/remoshock)


**How do I report bugs, feature requests and patches?**

Please use the GitHub issue tracker at
[https://github.com/remoshock/remoshock](https://github.com/remoshock/remoshock).


## ✔️ Requirements

**Will remoshock work on Microsoft Windows?**

remoshock works on Linux only. Ubuntu 2020.04 is used for testing.


**Which shocking devices are supported?**

- PAC collars (compatible with ATX and DTX remote, tested with ACX)
- Wodondog "Dog Shock Collar"
- Petrainer


**What transmitter hardware do I need?**

You need a SDR (software defined radio) device, that
- is able to transmit (most SDRs are receivers only)
- is able to operate on the required frequency (27.195 MHz for PAC)
- is supported by the software Universal Radio Hacker

According to Wikipedia both HackRF and LimeSDR fulfill those requirements.
HackRF is used for testing



## 🔍 Troubleshooting

**I am getting strange hardware error messages from my SDR transmitter**

Examples for error message:

~~~~
[CRITICAL::urh_cli.py::on_fatal_device_error_occurred] failed to start tx mode
[ERROR::Device.py::log_retcode] HackRF-SETUP
[ERROR::Device.py::log_retcode] HackRF-SETUP: HACKRF_ERROR_NOT_FOUND (-5)
[ERROR::Device.py::log_retcode] HackRF-SET_SAMPLE_RATE to 2M: HACKRF_ERROR_LIBUSB (-1000)
~~~~

Please avoid USB hubs and USB extension cables, but connect your SDR
directly to your computer. At least USB 2 hubs are known to be too
slow to sustain the bit-stream.

Please make sure that your computer is connected to the power network
(i. e. don't run your notebook on battery only). A throttled CPU
might be too slow to generate the bit-stream for the SDR.

If you run Linux inside of a Virtual Machine on a slow computer, you
might experience the same performance problems. VirtualBox only supports
USB 1.x in the default installation. Please see 
[https://www.eltima.com/article/virtualbox-usb-passthrough/](https://www.eltima.com/article/virtualbox-usb-passthrough/).


**Access to HackRF only works as root**

Access to the HackRF hardware only works as root. remoshock crashes with
either a segmentation fault or the following error message:

~~~~
[ERROR::Device.py::log_retcode] HackRF-SETUP: HACKRF_ERROR_NOT_FOUND (-5)
~~~~

The `hackrf_info` fails with the following error as a normal user:

~~~~
hackrf_open() failed: Access denied (insufficient permissions) (-1000)
~~~~

In order to access the hardware as normal user, a udev rule is needed.
Please create the file /etc/udev/rules.d/53-hackrf.rules with the
content from
https://raw.githubusercontent.com/mossmann/hackrf/master/host/libhackrf/53-hackrf.rules

Furthermore please make sure that the user in the group plugdev.


**It is not working, why?**

Please add the parameter `--verbose`. It will enable debug logging.


**I am in a VirtualBox VM and lsusb does not find my SDR transmitter**

Please see [https://www.eltima.com/article/virtualbox-usb-passthrough/](https://www.eltima.com/article/virtualbox-usb-passthrough/) on how to install and enable USB Passthrough support for VirtualBox.

In short:
- `apt install virtualbox-ext-pack`
- add yourself to the vboxuser group
- on the USB settings pages of the virutal machine select USB 3.0 controller
  and add a filter to allow access to the SDR device


**Which setup is used for testing?**

I use Ubuntu 2020.04 with a HackRF transmitter, a PAC ACX collar and
a brandless Wodondog collar.
