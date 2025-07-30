import importlib
import typing
import types


def serialize_callable(func: typing.Callable) -> dict:
    """Serialize a callable object to "callable" dictionary.
    Data are saved that allow you to “recreate” the function.
    The body of the function is not saved.

    Args:
        func: Any callable function

    Returns:
        dict: An callable function serialized as a dict, which can be stored in Text format.
    """
    data = {
        "module": func.__module__,
        "qualname": func.__qualname__,
    }

    if isinstance(func, types.MethodType) and hasattr(func, "__self__"):
        instance = func.__self__
        if instance is not None and not isinstance(instance, type):
            data["instance_required"] = True
            try:
                instance_attrs = {}
                for k, v in vars(instance).items():
                    if not callable(v) and not k.startswith("_"):
                        instance_attrs[k] = v
                    elif callable(v):
                        instance_attrs[k] = serialize_callable(v)
                data["instance_attributes"] = instance_attrs
            except Exception as e:
                print(f"Could not serialize attributes: {e}")

    elif "." in func.__qualname__ and not isinstance(func, type):
        data["instance_required"] = True

    return data


def deserialize_callable(data: dict) -> typing.Callable:
    """Deserialize a callable dictionary to callable function.
    The function must be present in the code and in the same location.

    Args:
        data: A callable dictionary.

    Returns:
        func: A callable function.
    """
    module = importlib.import_module(data["module"])
    path = data["qualname"].split(".")

    if data.get("instance_required"):
        # Example: MyClass.method -> ['MyClass', 'method']
        cls_path = path[:-1]
        method_name = path[-1]

        # Get Class
        cls = module
        for attr in cls_path:
            cls = getattr(cls, attr)

        if 'instance_attributes' in data:
            instance_attributes = data['instance_attributes']
            instance = cls(**instance_attributes)

        else:
            instance = cls()  # Constructor w/o args
        return getattr(instance, method_name)
    else:
        obj = module
        for attr in path:
            obj = getattr(obj, attr)
        return obj