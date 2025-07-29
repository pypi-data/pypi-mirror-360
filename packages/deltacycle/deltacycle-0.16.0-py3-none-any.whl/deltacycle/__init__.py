"""Delta Cycle

Credit to David Beazley's "Build Your Own Async" tutorial for inspiration:
https://www.youtube.com/watch?v=Y4Gt3Xjd7G8
"""

import logging
from logging import Filter, LogRecord

from ._event import Event, EventList
from ._loop import Loop, finish
from ._queue import Queue
from ._semaphore import BoundedSemaphore, Lock, Semaphore
from ._task import (
    Interrupt,
    Predicate,
    Signal,
    Task,
    TaskCoro,
    TaskGroup,
)
from ._top import (
    any_event,
    any_var,
    create_task,
    get_current_task,
    get_loop,
    get_running_loop,
    irun,
    now,
    run,
    set_loop,
    sleep,
)
from ._variable import Aggregate, AggrItem, AggrValue, Singular, Value, Variable

# Customize logging
logger = logging.getLogger(__name__)


class DeltaCycleFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        try:
            loop = get_running_loop()
        except RuntimeError:
            record.time = -1
            record.taskName = None
        else:
            record.time = loop.time()
            record.taskName = loop.task().name
        return True


logger.addFilter(DeltaCycleFilter())


__all__ = [
    # loop
    "Loop",
    "finish",
    "get_running_loop",
    "get_loop",
    "set_loop",
    "run",
    "irun",
    "now",
    "sleep",
    # event
    "Event",
    "EventList",
    "any_event",
    # queue
    "Queue",
    # semaphore
    "Semaphore",
    "BoundedSemaphore",
    "Lock",
    # task
    "Predicate",
    "TaskCoro",
    "Signal",
    "Interrupt",
    "Task",
    "TaskGroup",
    "create_task",
    "get_current_task",
    # variable
    "Variable",
    "Value",
    "Singular",
    "Aggregate",
    "AggrItem",
    "AggrValue",
    "any_var",
]
