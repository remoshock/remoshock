#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________

import datetime

from remoshock.scheduler.task import Task


class CommandTask(Task):
    """A remoshock-command task that can be scheduled"""


    def __init__(self, timestamp, identifier, group_identifier, remoshock, receiver, action, power, duration):
        """a schedulable task object

        @param timestamp when this task should be executed
        @param identifier a unique identifier, which may be used to cancel the task before it is executed
        @param group_identifier an identifier, which may be used to cannel all task with same same group identifier
        @param remoshock reference to remoshock manager class
        @param receiver index of remoshock receiver
        @param action Action (e. g. BEEP, SHOCK)
        @param power power level (0-100)
        @param duration duration in ms
        """

        super().__init__(timestamp, identifier, group_identifier)
        self.remoshock = remoshock
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
        self.remoshock.command(self.receiver, self.action, self.power, self.duration)
