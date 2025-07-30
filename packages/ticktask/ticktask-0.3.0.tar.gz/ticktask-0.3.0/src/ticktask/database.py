from abc import ABC, abstractmethod
import typing
from .task import Task


class ISchedulerDatabase(ABC):

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def insert_task(self, task: Task) -> None:
        pass

    @abstractmethod
    def get_task(self, task_name: str) -> Task:
        pass

    @abstractmethod
    def get_all_tasks(self) -> typing.List[Task]:
        pass

    @abstractmethod
    def delete_task(self, task_name: str) -> bool:
        pass

    @abstractmethod
    def custom_query(self, query: typing.Dict) -> typing.Any:
        pass