#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________

import datetime

from pyshock.scheduler.task import Task


class CommandTask(Task):
    """A pyshock-command task that can be scheduled"""


    def __init__(self, timestamp, identifier, group_identifier, pyshock, receiver, action, power, duration):
        """a schedulable task object

        @param timestamp when this task should be executed
        @param identifier a unique identifier, which may be used to cancel the task before it is executed
        @param group_identifier an identifier, which may be used to cannel all task with same same group identifier
        @param pyshock reference to pyshock manager class
        @param receiver index of pyshock receiver
        @param action Action (e. g. BEEP, SHOCK)
        @param power power level (0-100)
        @param duration duration in ms
        """

        super().__init__(timestamp, identifier, group_identifier)
        self.pyshock = pyshock
        self.receiver = receiver
        self.action = action
        self.power = power
        self.duration = duration


    def __call__(self):
        """executes the task"""
        super().__call__()

        # if this call is really outdated, skip it (e. g. don't execute
        # all delayed calles as batch after the computer wakes up from hibernation)
        delayed = (datetime.datetime.now() - self.timestamp).total_seconds()
        if delayed > 30:
            return
        self.pyshock.command(self.receiver, self.action, self.power, self.duration)
