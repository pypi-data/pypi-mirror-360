import pytest
import time
import datetime
from src.ticktask import Scheduler, Task, TaskType


class TestVariables:
    var: int = 0


def mock_task_fun():
    TestVariables.var += 1


def test_start_scheduler():
    scheduler = Scheduler()
    scheduler.start()
    assert scheduler._Scheduler__main_loop_thread is not None
    assert scheduler._Scheduler__running is True
    scheduler.stop()


def test_stop_scheduler():
    scheduler = Scheduler()
    scheduler.start()
    time.sleep(0.1)
    scheduler.stop()
    assert scheduler._Scheduler__main_loop_thread is None
    assert scheduler._Scheduler__running is False


def test_add_task():
    test_task_name = "TestTask"
    test_task = Task(name=test_task_name, task=mock_task_fun)
    scheduler = Scheduler()
    scheduler.add_task(test_task)
    assert test_task in scheduler._Scheduler__task_list


def test_remove_task():
    test_task_name = "TestTask"
    test_task = Task(name=test_task_name, task=mock_task_fun)
    scheduler = Scheduler()
    scheduler.add_task(test_task)
    scheduler.remove_task(test_task_name)
    assert not test_task in scheduler._Scheduler__task_list


def test_get_task():
    test_task_name = "TestTask"
    test_task = Task(name=test_task_name, task=mock_task_fun)
    scheduler = Scheduler()
    scheduler.add_task(test_task)
    get_task = scheduler.get_task(test_task_name)
    assert len(scheduler.get_task_list()) == 1
    assert test_task == get_task


def test_add_task_one_time():
    TestVariables.var = 0
    test_task_name = "TestTask"
    test_task = Task(name=test_task_name, task=mock_task_fun)
    assert TestVariables.var == 0
    scheduler = Scheduler()
    scheduler.start()
    scheduler.add_task(test_task)
    time.sleep(0.1)
    assert TestVariables.var == 1
    scheduler.stop()


def test_add_task_repeat():
    TestVariables.var = 0
    test_time_interval = 333
    test_task_name = "TestTask"
    test_task = Task(name=test_task_name, task=mock_task_fun, task_type=TaskType.REPEAT, time_interval=datetime.timedelta(milliseconds=test_time_interval))
    temp_stage_zero = TestVariables.var
    scheduler = Scheduler()
    scheduler.start()
    scheduler.add_task(test_task)
    time.sleep(0.1)
    temp_stage_one = TestVariables.var
    time.sleep(0.1 + (test_time_interval/1000))
    temp_stage_two = TestVariables.var
    scheduler.stop()
    assert temp_stage_zero == 0
    assert temp_stage_one == 1
    assert temp_stage_two == 2


def test_clear_thread_list():
    test_task_name = "TestTask"
    test_task = Task(name=test_task_name, task=mock_task_fun)
    scheduler = Scheduler()
    scheduler.start()
    scheduler.add_task(test_task)
    time.sleep(0.3)
    assert len(scheduler._Scheduler__task_list_thread) == 0
    scheduler.stop()


if __name__ == '__main__':
    pytest.main()