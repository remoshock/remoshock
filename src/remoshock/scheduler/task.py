#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________

import secrets
import string
from remoshock.scheduler.scheduler import scheduler


class Task:
    """A task that can be scheduled"""

    def __init__(self, timestamp, identifier=None, group_identifier=None):
        """a schedulable task object

        @param timestamp when this task should be executed
        @param identifier a unique identifier, which may be used to cancel the task before it is executed
        @param group_identifier an identifier, which may be used to cannel all task with same same group identifier
        """
        self.timestamp = timestamp
        self.identifier = identifier
        if identifier is None:
            charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
            self.identifier = ''.join(secrets.choice(charset) for _ in range(40))
        self.group_identifier = group_identifier


    def __call__(self):
        """executes the task"""
        scheduler().internal_cleanup_task(self)
