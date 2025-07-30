import typing
import enum
import datetime
import threading


class TaskType(enum.Enum):
    ONE_TIME = 1
    REPEAT = 2


class Task:

    __hash__ = None

    def __init__(self,
            name: str,
            task: typing.Callable,
            task_type: TaskType = None,
            task_args: typing.Dict[str, typing.Any] = None,
            start_date: datetime.datetime = None,
            time_interval: datetime.timedelta = None,
            callback: typing.Callable = None,
            callback_args: typing.Dict[str, typing.Any] = None
            ) -> None:
        """Create a new Task object.

        Args:
            name (str): The name of the task.
            task (typing.Callable): The task function.
            task_type (TaskType, optional): The task type.
            task_args (typing.Dict[str, typing.Any], optional): The arguments of the task.
            start_date (datetime.datetime, optional): The start date of the task.
            time_interval (datetime.timedelta, optional): The time interval of the task.
            callback (typing.Callable, optional): The callback function.
            callback_args (typing.Dict[str, typing.Any], optional): The arguments of the callback.
        """
        self.name = name
        self.task = task
        self.task_type = task_type if task_type is not None else TaskType.ONE_TIME
        self.task_args = task_args if task_args is not None else {}
        self.start_date = start_date if start_date is not None else datetime.datetime.now()
        self.time_interval = time_interval
        self.callback = callback
        self.callback_args = callback_args if callback_args is not None else {}
        self.output: typing.Any = None

    def __repr__(self) -> str:
        args_str = ", ".join(f"{key}={value}" for key, value in self.task_args.items())
        return (f"<Task \"{self.name}\" start {self.task.__name__}({args_str})"
                f" at {self.start_date.strftime('%Y-%m-%d %H:%M:%S')}>")

    def __str__(self) -> str:
        """Returns the name of the task.
        """
        return f"{self.name}"

    def __call__(self) -> None:
        self.exec()

    def exec_in_main_thread(self) -> None:
        """Execute the task now in the main thread, ignore putted time.
        If Callback has arg "<task_name>_output" then output from
        task will assign to this callback argument.
        """
        self.output = self.task(**self.task_args)
        if self.task.__name__ + "_output" in self.callback_args.keys():
            self.callback_args[self.task.__name__ + "_output"] = self.output
        if self.callback is not None:
            self.callback(**self.callback_args)

    def exec(self) -> None:
        """Execute the task now in new thread and don't stop code, ignore putted time.
        If Callback has arg "<task_name>_output" then output from
        task will assign to this callback argument.
        """
        thread = threading.Thread(target=self.exec_in_main_thread)
        thread.start()