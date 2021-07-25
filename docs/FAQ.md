# Frequently asked Questions and answers

## ⚠️ Risks

**Is playing with electricity dangerous?**

Yes, it is. Please see [WARNING](https://github.com/pyshock/pyshock/blob/master/doc/WARNING.md)


**Should I play with electricity?**

No, you should not. Please see [WARNING](https://github.com/pyshock/pyshock/blob/master/doc/WARNING.md)



## 🔧 About the project

**Where can I find documentation and source code?**

[https://github.com/pyshock/pyshock](https://github.com/pyshock/pyshock)


**How do I report bugs, feature requests and patches?**

Please use the GitHub issue tracker at
[https://github.com/pyshock/pyshock](https://github.com/pyshock/pyshock).


## ✔️ Requirements

**Will pyshock work on Microsoft Windows?**

pyshock works on Linux only. Ubuntu 2020.04 is used for testing.


**Which shocking devices are supported?**

At the time of writing, only PAC collars of type ACX are tested.
BCX collars (the smaller ones) are supposed to work as they
can be controlled by the same remote (ATX, DTX).

Support for other vendors might be added at a later time. pyshock
is designed with this kind of extension in mind. 


**What transmitter hardware do I need?**

You need a SDR (software defined radio) device, that
- is able to transmit (most SDRs are receivers only)
- is able to operate on the required frequency (27.195 MHz for PAC)
- is supported by the software Universal Radio Hacker

According to Wikipedia both HackRF and LimeSDR fulfill those requirements.
HackRF is used for testing



## 🔍 Troubleshooting

**I am getting strange hardware error messages from my SDR transmitter**

~~~~
[CRITICAL::urh_cli.py::on_fatal_device_error_occurred] failed to start tx mode
[ERROR::Device.py::log_retcode] HackRF-SETUP
~~~~

Please avoid USB hubs and connect your SDR directly to your computer.
At least USB 2 hubs are known to be too slow to sustain the bit-stream.

If you run Linux inside of a Virtual Machine on a slow computer, you
might experience the same performance problems. VirtualBox only supports
USB 1.x in the default installation. Please see 
[https://www.eltima.com/article/virtualbox-usb-passthrough/](https://www.eltima.com/article/virtualbox-usb-passthrough/).


**It is not working, why?**

Please add the parameter `--verbose`. It will enable debug logging.


**I am in a VirtualBox VM and lsusb does not find my SDR transmitter**

Please see [https://www.eltima.com/article/virtualbox-usb-passthrough/](https://www.eltima.com/article/virtualbox-usb-passthrough/) on how to install and enable USB Passthrough support for VirtualBox.

Note: I did not work for me. USB 3.0 showed up after
`apt install virtualbox-ext-pack`, adding myself to the vboxuser group and
restarting. But the VirtualBox Machine configuration dialog does not 
list any USB devices. Neither does `lsusb` inside the virtual machine.


**Which setup is used for testing?**

I use Ubuntu 2020.04 with a HackRF transmitter and a PAC ACX collar.