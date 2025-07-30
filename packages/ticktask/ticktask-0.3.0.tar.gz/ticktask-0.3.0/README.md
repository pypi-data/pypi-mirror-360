# TickTask
**TickTask** is a lightweight and intuitive Python library designed to execute functions at
specified times. Whether you're looking to automate tasks, schedule reminders,
or perform time-based operations, TickTask provides a simple interface to schedule
function calls with ease.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Changelog](#changelog)
- [TODO](#todo)
- [License](#license)

## Installation
To install TickTask, make sure you have Python version 3.12 or higher installed on your system.

### Unix/macOS
```bash
pip3 install ticktask
```

### Windows
```bash
pip install ticktask
```

## Usage
### Scheduler Class
The Scheduler class is a core component of the TickTask library, responsible
for managing and executing scheduled tasks. It can operate with or without
a database, allowing for flexible task management.

#### Parameters
 - **database** `ISchedulerDatabase`, *optional*: An instance of a database 
   object that allows the scheduler to store and retrieve tasks.

#### Methods
Starts the scheduler. If a database is provided, it will
connect to the database and retrieve all existing tasks:
```python
start(self) -> None
```

Stops the scheduler. If a database is provided, it will disconnect from the database:
```python
stop(self) -> None
```

Adds a new task to the scheduler. If a task with the same
name already exists, a ValueError will be raised:
```python
add_task(self, task: Task) -> None
# task (Task): The task to be added to the scheduler.
```

Removes a task from the scheduler by its name. If the task
does not exist, a ValueError will be raised:
```python
remove_task(self, task_name: str) -> None
# task_name (str): The name of the task to be removed.
```

#### Example Usage
Here's an example of how to create a scheduler, add tasks, and start it:
```python
from ticktask import Scheduler, Task, TaskType

# Create a scheduler
scheduler = Scheduler()

# Define a task
def my_task():
    print("Task executed!")

task = Task(
    name="My Task",
    task=my_task
)

# Add the task to the scheduler
scheduler.add_task(task)

# Start the scheduler
scheduler.start()

# Stop the scheduler when done
scheduler.stop()
```

### Task Class
The Task class represents a scheduled task. It encapsulates the task's details,
including its name, the function to execute, and any arguments required for execution.

#### Parameters
 - **name** `str`: The name of the task.
 - **task** `typing.Callable`: The function to be executed as the task.
 - **task_type** `TaskType, optional`: The type of the task, either ONE_TIME or REPEAT.
   Defaults to ONE_TIME.
 - **task_args** `typing.Dict[str, typing.Any]`, *optional*: A dictionary of
   arguments to pass to the task function. Defaults to an empty dictionary.
 - **start_date** `datetime.datetime`, *optional*: The date and time when the
   task should start. Defaults to the current date and time.
 - **time_interval** `datetime.timedelta`, *optional*: The interval at which the
   task should repeat (if applicable).
 - **callback** `typing.Callable`, *optional*: A callback function to be executed
   after the task completes.
 - **callback_args** `typing.Dict[str, typing.Any]`, *optional*: A dictionary of 
   arguments to pass to the callback function.

#### Methods
```python
# New thread
exec()

# "Main" thread
exec_in_main_thread()
```
Executes the task immediately, ignoring any scheduled time. `exec()` run code in new thread
while `exec_in_main_thread()` run code in "main" thread and block code until finish.
If a callback is provided, it will be executed after the task completes, and the output
of the task can be passed to the callback if specified.

#### Example Usage
Here’s an example of how to create and execute a task using the Task class:

```python
import datetime
from ticktask import Task, TaskType

def my_function(arg1, arg2):
    print(f"Task executed with arguments: {arg1}, {arg2}")
    return arg1 + arg2

def my_callback(output):
    print(f"Callback executed with output: {output}")

# Create a task
task = Task(
    name="My First Task",
    task=my_function,
    task_type=TaskType.ONE_TIME,
    task_args={"arg1": 5, "arg2": 10},
    start_date=datetime.datetime.now(),
    callback=my_callback,
    callback_args={"output": None}
)

# Execute the task in new thread
task.exec()

# Or execute in the same "main" thread.
task.exec_in_main_thread()
```

### Callable Serialization
This module provides functionality to serialize and deserialize callable
objects in Python. The serialization process converts a callable into
a dictionary format that can be stored and later reconstructed, while
deserialization restores the callable from its dictionary representation.

**Warning**: These functions are in the experimental phase. They may
not handle all edge cases and should be used with caution in
production environments.

#### Functions
```python
serialize_callable(func: typing.Callable) -> dict
# func (typing.Callable): The function or callable object to serialize.
# dict: A dictionary containing the serialized representation of the callable.
```
Serializes a callable object into a dictionary format. This allows
you to store essential information required to recreate the function
later. Note that the body of the function is not saved, only metadata.

```python
deserialize_callable(data: dict) -> typing.Callable
# data (dict): The dictionary containing the serialized callable information.
# typing.Callable: The deserialized callable function.
```
Deserializes a dictionary back into a callable function. The function
must exist in the code and be located in the same module and path as
when it was serialized.

#### Usage Notes
Ensure that the functions you serialize are available in the same
module and path when deserializing. These functions do not serialize
the function's body or state, only its location and name. Use with
caution in production environments due to their experimental nature.

## ChangeLog

### [0.3.0] - 2025-07-07

#### Add

- Add new method for `Task` `exec_in_main_thread()` to run task in the "main" thread.

#### Change

- `exec()` method in `Task` now start task in new threads.

#### Fix

- In `deserialize_callable` there was a leftover from testing and was removed
  the print of class attributes when reconstructing method.

### [0.2.0] - 2025-06-30

#### Add

- Adding in `serialize_callable` and `deserialize_callable` the ability 
  to process methods from objects. Serialization saves attributes and
  their values. Object initialization should include initialization
  of all object attributes

### [0.1.2] - 2025-06-18

#### Fix

- In `__start_task` method remove calls `target`.

### [0.1.1] - 2025-06-17

#### Fix

- Use `remove_task` method to delete `ONE_TIME` task after executed.

### [0.1.0] - 2025-06-16

#### Initial Release

- Introduced basic library features.

## TODO

- Create a more intuitive method of passing shuffle output to a callback.
- ~~Add Status Codes.~~ Adding more exceptions for more control.
- To create a method of storing functions together with the body,
  maintaining security.

## License

This project is licensed under the terms of the MIT license. For more
details, please refer to the [LICENSE](LICENSE) file.