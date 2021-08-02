#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________

import time
import unittest
import datetime

from pyshock.scheduler.scheduler import scheduler
from pyshock.scheduler.task import Task


class MockTask(Task):
    """a mock task used for testing"""


    def __init__(self, timestamp, identifier, group_identifier):
        """creates a mock task

        @param timestamp when this task should be executed
        @param identifier a unique identifier, which may be used to cancel the task before it is executed
        @param group_identifier an identifier, which may be used to cannel all task with same same group identifier
        """
        super().__init__(timestamp, identifier, group_identifier)
        self.called = False


    def __call__(self):
        """remember that this task was processed"""
        super().__call__()
        self.called = True


class TestScheduler(unittest.TestCase):

    def test_scheduler_normal(self):
        """tests the normal opertion of the scheduler"""
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(milliseconds=1)
        mock_task = MockTask(timestamp + delta, "identifier", "group_identifier")
        scheduler().schedule_task(mock_task)

        # wait a little time and check that the task was executed
        time.sleep(.005)
        self.assertTrue(mock_task.called, "task was executed")


    def test_scheduler_cancel(self):
        """test cancelation of a task"""
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(milliseconds=10)
        mock_task = MockTask(timestamp + delta, "identifier", "group_identifier")
        scheduler().schedule_task(mock_task)
        scheduler().cancel_task("identifier")

        # wait a little time and check that the task was not executed
        time.sleep(.02)
        self.assertFalse(mock_task.called, "task was not executed")


    def test_group_scheduler_cancel(self):
        """test cancelation of all tasks in a  group"""
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(milliseconds=10)
        mock_task1 = MockTask(timestamp + delta, "identifier1", "group_identifier")
        scheduler().schedule_task(mock_task1)
        mock_task2 = MockTask(timestamp + delta, "identifier2", "other_group_identifier")
        scheduler().schedule_task(mock_task2)
        mock_task3 = MockTask(timestamp + delta, "identifier3", "group_identifier")
        scheduler().schedule_task(mock_task3)
        scheduler().cancel_group("group_identifier")

        # wait a little time and check that all tasks of the group were not executed,
        # also check that a task from another group was executed
        time.sleep(.02)
        self.assertFalse(mock_task1.called, "task was not executed")
        self.assertTrue(mock_task2.called, "task was executed")
        self.assertFalse(mock_task3.called, "task was not executed")
