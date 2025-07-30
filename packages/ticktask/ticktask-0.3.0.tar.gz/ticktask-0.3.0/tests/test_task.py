import pytest
import time
import datetime
from src.ticktask import Task, TaskType


class TestVariables:
    var1: int = 0
    var2: int = 0


def mock_function(var1: int):
    TestVariables.var1 += var1
    return TestVariables.var1


def mock_callback(mock_function_output: int):
    TestVariables.var2 = mock_function_output


def test_init_task():
    start_time = datetime.datetime.now()
    time_delta = datetime.timedelta(seconds=1)
    task_name = 'test_task'
    task_fun = mock_function
    task_type = TaskType.ONE_TIME
    task_args={"var1": 0}
    callback = mock_callback
    callback_args = {"mock_function_output": 0}
    task = Task(name=task_name, task=task_fun, task_args=task_args, callback=callback, callback_args=callback_args,
                task_type=task_type, start_date=start_time, time_interval=time_delta)
    assert task.name == task_name
    assert task.task == task_fun
    assert task.task_args == task_args
    assert task.callback == callback
    assert task.callback_args == callback_args
    assert task.task_type == task_type
    assert task.start_date == start_time
    assert task.time_interval == time_delta
    assert str(task) == task_name
    assert task_name in task.__repr__()


def test_task_execution():
    task_name = 'test_task'
    task_fun = mock_function
    task_args = {"var1": 1}
    TestVariables.var1 = 0
    task = Task(name=task_name, task=task_fun, task_args=task_args)
    task()
    time.sleep(0.1)
    assert TestVariables.var1 == 1


def test_task_execution_callback():
    task_name = 'test_task'
    task_fun = mock_function
    task_args = {"var1": 1}
    task_callback = mock_callback
    task_callback_args = {"mock_function_output": 0}
    TestVariables.var1 = 0
    TestVariables.var2 = 0
    task = Task(name=task_name, task=task_fun, task_args=task_args, callback=task_callback, callback_args=task_callback_args)
    task.exec()
    time.sleep(0.1)
    assert TestVariables.var1 == 1
    assert TestVariables.var2 == 1


if __name__ == '__main__':
    pytest.main()