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

If you do not want to create an account on GitHub, you can also reach me at 
https://fetlife.com/conversations/new?with=1561493



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
- is able to transmit (most SDR are only receivers)
- is able to operate on the required frequency (27.195 MHz for PAC)
- is supported by the software Universal Radio Hacker

According to Wikipedia both HackRF and LimeSDR fulfill those requirements.
HackRF is used for testing



## 🔍 Troubleshooting

**I am getting strange hardware error messages from my SDR transmitter**

Please avoid USB hubs and connect your SDR directly to your computer.
At least USB 2 hubs are known to be too slow to sustain the bit-stream.

If you run Linux inside of a Virtual Machine on a slow computer, you
might experience the same performance problems.



