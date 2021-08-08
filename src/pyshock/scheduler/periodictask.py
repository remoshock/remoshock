#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________

import datetime
from pyshock.scheduler.scheduler import scheduler


class PeriodicTask:
    """A task that will be repeated periodically"""

    def __init__(self, interval, task):
        """a wrapper task which schedules a task repeatedly

        @param interval interval in seconds
        @param task to execute
        """
        self.interval = interval
        self.timestamp = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() + interval)
        self.identifier = task.identifier
        self.group_identifier = task.group_identifier


    def __call__(self):
        """executes the task"""
        # do not call super in order not to clean up this task
        # we share the same identifier with the delegation task, so it
        # will do the cleanup for us
        self.task.__call__()

        self.timestamp = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() + self.interval)
        scheduler().schedule_task(self)
