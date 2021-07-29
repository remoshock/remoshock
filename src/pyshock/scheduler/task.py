#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________


class Task:
    """A task that can be scheduled"""


    def __init__(self, timestamp, identifier, group, receiver, action, power, duration):
        self.timestamp = timestamp
        self.identifier = identifier
        self.group = group
        self.receiver = receiver
        self.action = action
        self.power = power
        self.duration = duration
