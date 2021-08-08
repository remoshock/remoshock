#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________


import datetime
import threading


class Scheduler:
    """a scheduler for future tasks"""

    def __init__(self):
        self.__scheduled_tasks = {}
        self.__scheduled_task_references = {}
        self.__scheduled_groups = {}
        self.lock = threading.RLock()


    def schedule_task(self, task):
        """schedules a tasks for future processing

        @param task a task object
        @return true, if the task was scheduled, false otherwise
                (e. g. because timestamp was in the past"""

        with self.lock:
            wait_time = (task.timestamp - datetime.datetime.now()).total_seconds()
            if wait_time < 0:
                # timestamp is in the past
                return False

            timer_reference = threading.Timer(wait_time, task)
            self.__scheduled_tasks[task.identifier] = task
            self.__scheduled_task_references[task.identifier] = timer_reference
            if task.group_identifier is not None:
                if task.group_identifier in self.__scheduled_groups:
                    group = self.__scheduled_groups[task.group_identifier]
                else:
                    group = []
                    self.__scheduled_groups[task.group_identifier] = group
                group.append(task.identifier)

            timer_reference.daemon = True
            timer_reference.start()
            return True

    def internal_cleanup_task(self, task):
        """cleansup datastructure after tasks was executed or canceled.
        Do not call directly.

        @param task the task to cleanup"""

        with self.lock:
            self.__scheduled_tasks.pop(task.identifier, None)
            self.__scheduled_task_references.pop(task.identifier, None)

            if task.group_identifier is not None:
                if task.group_identifier in self.__scheduled_groups:
                    group = self.__scheduled_groups[task.group_identifier]
                    if task.identifier in group:
                        group.remove(task.identifier)
                        if len(group) == 0:
                            self.__scheduled_groups.pop(task.group_identifier, None)


    def cancel_task(self, identifer):
        """chancels a future task

        @param identifier identifier of this task"""

        with self.lock:
            if identifer in self.__scheduled_tasks:
                task = self.__scheduled_tasks.pop(identifer)
                timer_reference = self.__scheduled_task_references.pop(identifer, None)
                if timer_reference is not None:
                    timer_reference.cancel()
                self.internal_cleanup_task(task)


    def cancel_group(self, group_identifier):
        """chancels all future tasks belonging to the group

        @param group_identifier identifier of this group"""
        with self.lock:
            if group_identifier in self.__scheduled_groups:
                task_identifiers = self.__scheduled_groups.pop(group_identifier)
                for task_identifier in task_identifiers:
                    self.cancel_task(task_identifier)



__scheduler = None


def scheduler():
    """a scheduler for future tasks"""
    # singleton pattern
    global __scheduler
    if __scheduler is None:
        __scheduler = Scheduler()
    return __scheduler
