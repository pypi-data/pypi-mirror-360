import typing

import pytest
import time
import datetime
from src.ticktask import deserialize_callable, serialize_callable


def mock_callable(arg1: int, arg2: int):
    return arg1 + arg2


class MockClass:
    def mock_callable(self, arg1: int, arg2: int):
        return arg1 + arg2


class MockObject:
    def __init__(self, arg1: int, arg2: int):
        self.arg1 = arg1
        self.arg2 = arg2

    def mock_callable(self):
        return self.arg1 + self.arg2


def test_serialize_callable():
    test_callable = mock_callable
    test_module = "test_utils"
    test_qualname = "mock_callable"
    serialized_dict = serialize_callable(test_callable)
    assert serialized_dict['module'] == test_module
    assert serialized_dict['qualname'] == test_qualname


def test_deserialize_callable():
    test_module = "test_utils"
    test_qualname = "mock_callable"
    serialized_dict = {
        'module': test_module,
        'qualname': test_qualname,
    }
    restored_callable = deserialize_callable(serialized_dict)
    assert restored_callable(1, 1) == 2


def test_serialize_callable_class():
    test_callable = MockClass.mock_callable
    test_module = "test_utils"
    test_qualname = "MockClass.mock_callable"
    test_instance_required = True
    serialized_dict = serialize_callable(test_callable)
    assert serialized_dict['module'] == test_module
    assert serialized_dict['qualname'] == test_qualname
    assert serialized_dict['instance_required'] == test_instance_required


def test_deserialize_callable_class():
    test_module = "test_utils"
    test_qualname = "MockClass.mock_callable"
    test_instance_required = True
    serialized_dict = {
        'module': test_module,
        'qualname': test_qualname,
        'instance_required': test_instance_required,
    }
    restored_callable = deserialize_callable(serialized_dict)
    assert restored_callable(1, 1) == 2


def test_serialize_callable_object():
    test_module = "test_utils"
    test_qualname = "MockObject.mock_callable"
    test_instance_required = True
    test_instance_attributes = {'arg1': 1, 'arg2': 2}
    test_object = MockObject(1, 2)
    serialized_dict = serialize_callable(test_object.mock_callable)
    assert serialized_dict['module'] == test_module
    assert serialized_dict['qualname'] == test_qualname
    assert serialized_dict['instance_required'] == test_instance_required
    assert serialized_dict['instance_attributes'] == test_instance_attributes


def test_deserialize_callable_object():
    test_module = "test_utils"
    test_qualname = "MockObject.mock_callable"
    test_instance_required = True
    test_instance_attributes = {'arg1': 1, 'arg2': 2}
    serialized_dict = {
        'module': test_module,
        'qualname': test_qualname,
        'instance_required': test_instance_required,
        'instance_attributes': test_instance_attributes,
    }
    restored_callable = deserialize_callable(serialized_dict)
    assert restored_callable() == test_instance_attributes['arg2'] + test_instance_attributes['arg1']

if __name__ == "__main__":
    pytest.main()