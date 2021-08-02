#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________


class Task:
    """A task that can be scheduled"""


    def __init__(self, timestamp, identifier, group_identifier, receiver, action, power, duration):
        """a schedulable task object

        @param timestamp when this task should be executed
        @param identifier a unique identifier, which may be used to cancel the task before it is executed
        @param group_identifier an identifier, which may be used to cannel all task with same same group identifier
        @param receiver index of pyshock receiver
        @param action Action (e. g. BEEP, SHOCK)
        @param power power level (0-100)
        @param duration duration in ms
        """

        self.timestamp = timestamp
        self.identifier = identifier
        self.group_identifier = group_identifier
        self.receiver = receiver
        self.action = action
        self.power = power
        self.duration = duration
