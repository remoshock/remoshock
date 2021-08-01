#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________

import threading

from pyshock.scheduler.task import Task


def task_indexer(task):
    return task.timestamp


class Scheduler:

    def __init__(self):
        self.scheduled_tasks = []
        self.lock = threading.RLock()


    def add(self, tasks):
        with self.lock:
            if isinstance(tasks, list):
                for task in tasks:
                    self.scheduled_tasks.append(task)
            elif isinstance(tasks, Task):
                self.scheduled_tasks.append(tasks)
            else:
                raise Exception("Invalid type of parameter: " + str(tasks))

            self.scheduled_tasks.sort(task_indexer)


    def remove(self, identifier):
        with self.lock:
            for i in range(len(self.scheduled_tasks) - 1, -1, -1):
                if self.scheduled_tasks[i].identifier == identifier:
                    del self.scheduled_tasks[i]


    def remove_group(self, group):
        with self.lock:
            for i in range(len(self.scheduled_tasks) - 1, -1, -1):
                if self.scheduled_tasks[i].group == group:
                    del self.scheduled_tasks[i]


#    def start(self):
#        x = threading.Thread(target=thread_function, args=(1,), daemon=True)

#        t = threading.Timer(30.0, my_function)
#        keep dict with identifer and timer-reference, group-identifer and list of timer references
#        remove from dicts, from event handler
#
