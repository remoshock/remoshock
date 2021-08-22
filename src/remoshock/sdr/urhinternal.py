#
# Most code in this file is copied from https://github.com/jopohl/urh
# which is GPL. Please see https://github.com/jopohl/urh/blob/master/LICENSE
# __________________________________________________________________________

# flake8: noqa

import argparse
import datetime
import logging
import os
import sys
import time
import threading

import numpy as np

from remoshock.sdr.sdrsender import SdrSender
from remoshock.util.logutil import HidePrintIfNotVerbose

cli_exe = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
cur_dir = os.path.realpath(os.path.dirname(os.path.realpath(cli_exe)))
SRC_DIR = os.path.realpath(os.path.join(cur_dir, "..", "urh", "build", "lib.linux-x86_64-3.8"))

if os.path.isdir(SRC_DIR):
    sys.path.insert(0, SRC_DIR)

try:
    from urh.signalprocessing.IQArray import IQArray
except ModuleNotFoundError:
    print()
    print("ERROR: Could not import urh")
    print("Please install Universal Radio Hacker:")
    print("sudo apt install python3-pip python3-pyqt5; sudo pip3 install urh")
    print()
    print("If URH is installed, you may try to use the command line interface")
    print("instead of internal invokation by editing remoshock.ini:")
    print("sdr=HackRFcli")
    print();
    sys.exit(1)

from urh.util import util

util.set_shared_library_path()

from urh.util import Logger
from urh.util.Logger import logger

from urh.cli import urh_cli
from urh.dev.native.lib import hackrf
from multiprocessing import Array


log_enabled = False

def log(msg):
    if log_enabled:
        print(str(datetime.datetime.now().time()) + " " + msg)


class SendConfig:
    def __init__(self, send_buffer, total_samples: int):
        self.send_buffer = send_buffer
        self.total_samples = total_samples
        self.current_sent_index = 0


    def get_data_to_send(self, buffer_length: int):
        try:
            if self.sending_is_finished():
                return np.zeros(1, dtype=self.send_buffer._type_._type_)

            index = self.current_sent_index
            np_view = np.frombuffer(self.send_buffer, dtype=self.send_buffer._type_._type_)
            result = np_view[index:index + buffer_length]

            self.progress_send_status(len(result))
            return result
        except (BrokenPipeError, EOFError):
            return np.zeros(1, dtype=self.send_buffer._type_._type_)


    def sending_is_finished(self):
        return self.current_sent_index >= self.total_samples


    def progress_send_status(self, buffer_length: int):
        self.current_sent_index += buffer_length
        if self.current_sent_index >= self.total_samples - 1:
            self.current_sent_index = self.total_samples



class Sender:

    def __init__(self):
        DEFAULT_CARRIER_AMPLITUDE = 1
        DEFAULT_CARRIER_PHASE = 0
        DEFAULT_NOISE = 0.1
        DEFAULT_CENTER = 0
        DEFAULT_CENTER_SPACING = 0.1
        DEFAULT_TOLERANCE = 5

        args = argparse.Namespace()
        args.receive = False
        args.transmit = True
        args.filename = None
        args.encoding = None
        args.hex = False
        args.pause = 262924
        args.gain = 47 #None
        args.if_gain = 47 #None
        args.bandwidth = None
        args.baseband_gain = None
        args.modulation_type = "FSK"
        args.samples_per_symbol = 3100
        args.center = DEFAULT_CENTER
        args.center_spacing = DEFAULT_CENTER_SPACING
        args.noise = DEFAULT_NOISE
        args.tolerance = DEFAULT_TOLERANCE
        args.bits_per_symbol = 1
        args.carrier_frequency = 27.1e6
        args.carrier_amplitude = DEFAULT_CARRIER_AMPLITUDE
        args.carrier_phase = DEFAULT_CARRIER_PHASE
        args.parameters = [92e3, 95e3]
        args.device_backend = "native"
        args.device = "HackRF"
        args.device_identifier = None
        args.frequency = 27.1e6
        args.frequency_correction = 1
        args.sample_rate = 2e6
        args.raw = False

        logger.setLevel(logging.ERROR)
        #logger.setLevel(logging.INFO)
        #logger.setLevel(logging.DEBUG)
        Logger.save_log_level()

        self.args = args
        hackrf.setup(None)
        self.reset()


    def reset(self):
        bandwidth = self.args.sample_rate if self.args.bandwidth is None else self.args.bandwidth
        gain = 20 if self.args.gain is None else self.args.gain
        if_gain = 20 if self.args.if_gain is None else self.args.if_gain

        hackrf.TIMEOUT = 0
        hackrf.set_freq(self.args.frequency)
        hackrf.set_sample_rate(self.args.sample_rate)
        hackrf.set_baseband_filter_bandwidth(bandwidth)
        hackrf.set_rf_gain(gain)
        hackrf.set_if_tx_gain(if_gain)
        hackrf.TIMEOUT = 0.1


    def modulate_messages(self, messages):
        log("modulate messages")
        self.args.messages = [messages]
        messages_to_send = urh_cli.read_messages_to_send(self.args)
        modulator = urh_cli.build_modulator_from_args(self.args)
        samples = urh_cli.modulate_messages(messages_to_send, modulator)
        log("modulate messages done")
        return samples

    @staticmethod
    def iq_to_bytes(samples: np.ndarray):
        arr = Array("B", 2 * len(samples), lock=False)
        numpy_view = np.frombuffer(arr, dtype=np.uint8)
        numpy_view[:] = samples.flatten(order="C")
        return arr


    def init_send_parameters(self, samples_to_send: IQArray):
        samples_to_send_ = samples_to_send.convert_to(np.int8)
        send_buffer = self.iq_to_bytes(samples_to_send_)
        total_samples = len(send_buffer)
        return SendConfig(send_buffer, total_samples)


    def send(self, samples_to_send: np.ndarray):
        send_config = self.init_send_parameters(samples_to_send)
        log("send config generated")

        try:
            ret = hackrf.start_tx_mode(send_config.get_data_to_send)
            log("hackrf.start_tx_mode")
            if ret != 0:
                print("ERROR: enter_async_send_mode failed")
                return False

            while not send_config.sending_is_finished():
                try:
                    time.sleep(0.01)
                except KeyboardInterrupt:
                    pass
            log("send completed")
        finally:
            time.sleep(0.2)
            hackrf.stop_tx_mode()
        log("send mode stopped")
        self.reset()
        log("send reset done")


    def shutdown_device(self):
        hackrf.close()
        hackrf.exit()



lock = threading.RLock()


class UrhInternalSender(SdrSender):
    """sends commands by directly invoking code from Universal Radio Hacker.

    This code prevents a 1 second delay before each transmission when using
    HackRF devices. However, it might cause Python errors, if URH is updated"""

    def __init__(self, verbose):
        global log_enabled
        log_enabled = verbose
        self.verbose = verbose
        self.sender = Sender()


    def send(self, frequency, sample_rate, carrier_frequency, 
             modulation_type, samples_per_symbol, low_frequency,
             high_frequency, pause, data):

        with lock:
            self.sender.args.pause = pause
            self.sender.args.modulation_type = modulation_type
            self.sender.args.samples_per_symbol = samples_per_symbol
            self.sender.args.carrier_frequency = carrier_frequency
            self.sender.args.parameters = [low_frequency, high_frequency]
            self.sender.args.sample_rate = sample_rate
            self.sender.args.frequency = frequency
            self.sender.reset()

            with HidePrintIfNotVerbose(self.verbose):
                samples = self.sender.modulate_messages(data)
                self.sender.send(samples)


if __name__ == '__main__':
    sender = Sender()

    try:
        samples_to_send = sender.modulate_messages(sys.argv[1])
        print(str(len(samples_to_send)))
        sender.send(samples_to_send)
        time.sleep(1)

        sender.send(samples_to_send)

    finally:
        sender.shutdown_device()
