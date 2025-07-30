import threading
import time
import datetime
import typing
from .task import Task, TaskType
from .database import ISchedulerDatabase


class Scheduler:

    def __init__(self, database:ISchedulerDatabase = None) -> None:
        """Initialize and start the scheduler. If database is putted
        then the scheduler will work with database.

        Args:
            database (ISchedulerDatabase instance, optional): database object.
        """
        # self.__start_time: datetime.datetime = datetime.datetime.now()
        self.__running: bool = False
        self.__current_time: datetime.datetime = datetime.datetime.now()
        self.__task_list: typing.List[Task] = []
        self.__task_list_thread: typing.List[threading.Thread] = []
        self.__database: ISchedulerDatabase = database
        self.__main_loop_thread: threading.Thread = None

    def __del__(self) -> None:
        """Close the scheduler if it is running.
        """
        self.stop()

    def __check_task(self) -> None:
        """Loop which look all task  and check witch task can start.
        If task type is TaskType.ONE_TIME_TASK, after start remove it from list.
        """
        for task in self.__task_list:
            if task.start_date < self.__current_time:
                if task.task_type == TaskType.ONE_TIME:
                    self.remove_task(task_name=task.name)
                else:
                    task.start_date += task.time_interval
                self.__start_task(task)

    def __clear_task_threads(self) -> None:
        """Clear task threads.
        """
        for task in self.__task_list_thread:
            if not task.is_alive():
                self.__task_list_thread.remove(task)

    def __main_loop(self) -> None:
        """Main loop of scheduler.
        """
        while self.__running:
            # Static cooldown
            time.sleep(0.03)

            # Get current time every loop
            self.__current_time = datetime.datetime.now()

            self.__check_task()

            self.__clear_task_threads()

        # After finish main_loop disconnect DB
        if self.__database:
            self.__database.disconnect()

    def __start_task(self, task: Task) -> threading.Thread:
        """Start task in new thread.

        Args:
            task: Task to start.

        Returns: Thread started Task.

        """
        task_thread = threading.Thread(target=task.exec)
        task_thread.start()
        self.__task_list_thread.append(task_thread)
        return task_thread

    def __start_scheduler(self) -> threading.Thread:
        """Start main loop of scheduler.
        """
        my_thread = threading.Thread(target=self.__main_loop)
        my_thread.start()
        return my_thread

    def start(self) -> None:
        """Start scheduler and if database is putted will connect.
        """
        # Check if scheduler is working
        if self.__running:
            return

        if self.__database:
            self.__database.connect()
            self.__database.get_all_tasks()

        # Start scheduler
        self.__running = True
        main_loop_thread = self.__start_scheduler()
        self.__main_loop_thread = main_loop_thread

    def stop(self) -> None:
        """Stop scheduler and if database is putted will disconnect.
        """
        # Check if scheduler is not working
        if not self.__running:
            return

        if self.__database:
            self.__database.disconnect()

        self.__running = False
        self.__main_loop_thread.join()
        self.__main_loop_thread = None

    def get_task_list(self) -> typing.List[Task]:
        """Get task list.

        Returns:
            typing.List[Task]: List with task list.
        """
        return self.__task_list

    def get_task(self, task_name: str) -> Task | None:
        """Get task by name.

        Args:
            task_name: Task name.

        Returns:
            Task: Task object.
        """
        for task in self.__task_list:
            if task.name == task_name:
                return task
        return None

    def add_task(self, task:Task) -> None:
        """Add task to scheduler.

        Args:
            task: Task
        """
        exists = any(t.name == task.name for t in self.__task_list)
        if exists:
            raise ValueError(f"A task named \"{task.name}\" already exists."
                             f" The name of the Task, must be unique!")
        else:
            self.__task_list.append(task)
            if self.__database:
                self.__database.insert_task(task)

    def remove_task(self, task_name: str) -> None:
        """Remove task from scheduler.

        Args:
            task_name: Remove task name.
        """
        exists = any(t.name == task_name for t in self.__task_list)
        if exists:
            self.__task_list = [task for task in self.__task_list if task.name != task_name]
            if self.__database:
                self.__database.delete_task(task_name)
            return
        else:
            raise ValueError(f"A task named \"{task_name}\" does not exist.")