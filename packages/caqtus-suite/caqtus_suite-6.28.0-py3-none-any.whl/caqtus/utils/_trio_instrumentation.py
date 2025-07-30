import traceback
from logging import Logger

import trio
from trio.abc import Instrument
from trio.lowlevel import Task


class LogBlockingTaskInstrument(Instrument):
    """A :class:`trio.abc.Instrument` loging a warning if a task doesn't yield for a
    long time.

    This is useful to detect tasks that might be blocking and prevent the event loop to
    respond to other tasks in a timely manner.

    Args:
        duration: The duration in seconds after which a warning should be logged.
        logger: The logger to use for logging the warning.
    """

    def __init__(self, duration: float, logger: Logger):
        self.duration = duration
        self.logger = logger
        self.step_before_times = dict[Task, float]()

    def before_task_step(self, task: Task) -> None:
        self.step_before_times[task] = trio.current_time()

    def after_task_step(self, task: Task) -> None:
        before_step_time = self.step_before_times.pop(task)
        elapsed = trio.current_time() - before_step_time
        if elapsed > self.duration:
            currently_waiting_on = task.coro.cr_frame  # type: ignore[reportAttributeAccessIssue]
            if currently_waiting_on is not None:
                formatted_stack = "".join(
                    traceback.StackSummary.extract(task.iter_await_frames()).format()
                )
                self.logger.warning(
                    "Task %r blocked the event loop for %.4f seconds.\n"
                    "This occurred just before this await point\n%s",
                    task,
                    elapsed,
                    formatted_stack,
                )
            else:
                self.logger.warning(
                    "Task %r blocked the event loop for %.4f seconds.\n"
                    "This occurred after the last await point of the task.",
                    task,
                    elapsed,
                )

        task.custom_sleep_data = None
