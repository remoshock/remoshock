#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________


from pyshock.scheduler.scheduler import scheduler


class Task:
    """A task that can be scheduled"""

    def __init__(self, timestamp, identifier, group_identifier):
        """a schedulable task object

        @param timestamp when this task should be executed
        @param identifier a unique identifier, which may be used to cancel the task before it is executed
        @param group_identifier an identifier, which may be used to cannel all task with same same group identifier
        """
        self.timestamp = timestamp
        self.identifier = identifier
        self.group_identifier = group_identifier


    def __call__(self):
        """executes the task"""
        scheduler().internal_cleanup_task(self)
