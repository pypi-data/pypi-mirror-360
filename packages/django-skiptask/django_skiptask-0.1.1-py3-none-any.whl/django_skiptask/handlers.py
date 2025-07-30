from concurrent.futures import ThreadPoolExecutor
from django.db import connections
from importlib import import_module
from typing import Tuple
import inspect

from .models import Task, Queueable
from .services import enqueue_task


class HandlerRegistry:
    """Handler registry is a key value store for looking up all registered handlers."""

    def __init__(self):
        self.registry = {}

    def register(self, handler_cls):
        key = handler_cls.get_handler_key()
        self.registry[key] = handler_cls

    def get(self, key):
        return self.registry.get(key, None)


registry = HandlerRegistry()


class Handler:
    @classmethod
    def get_handler_key(cls):
        return f"{cls.__module__}.{cls.__name__}"

    def handle(self, *args, **kwargs):
        raise RuntimeError("Handle not implemented.")

    def enqueue(self, *args, **kwargs):
        raise RuntimeError("Enqueue not implemented. ")


def connection_cleanup(future):
    connections.close_all()


def run_task(task: Task):
    task_args = task.payload.get("args", [])
    task_kwargs = task.payload.get("kwargs", {})

    module = import_module(task.payload["module"])
    name = task.payload["name"]

    if "." in name:
        cls_name, func_name = name.split(".")
        cls = getattr(module, cls_name)
        func_or_class = getattr(cls, func_name)
    else:
        func_or_class = getattr(module, name)

    if inspect.isfunction(func_or_class):
        task_callable = func_or_class
    elif inspect.isclass(func_or_class):
        task_callable = func_or_class.run
    elif inspect.ismethod(func_or_class):
        task_callable = func_or_class
    else:
        raise RuntimeError("Not a callable function or Task class.")

    # Run in a separate thread to ensure db connection isolation between
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(task_callable, *task_args, **task_kwargs)
        future.add_done_callback(connection_cleanup)
        result_value = future.result(timeout=float(task.run_timeout))
    return result_value


def enqueue_callable(
    func_or_class, args=None, kwargs=None, **local_kwargs
) -> Tuple[Queueable, Task]:
    if inspect.isfunction(func_or_class):
        func_or_class_key = func_or_class.__name__
    elif inspect.isclass(func_or_class):
        func_or_class_key = func_or_class.__name__
    elif inspect.ismethod(func_or_class):
        # SomeClass.run
        class_name = func_or_class.__self__.__name__
        func_name = func_or_class.__name__
        func_or_class_key = f"{class_name}.{func_name}"
    else:
        raise RuntimeError("Not a callable function or Task class.")

    module_key = func_or_class.__module__

    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    payload = {
        "module": module_key,
        "name": func_or_class_key,
        "args": args,
        "kwargs": kwargs,
    }
    return enqueue_task(PythonHandler, payload=payload, **local_kwargs)


class PythonHandler(Handler):
    def handle(self, task: Task):
        return run_task(task)

    def enqueue(self, *args, **kwargs):
        return enqueue_callable(*args, **kwargs)


registry.register(PythonHandler)
