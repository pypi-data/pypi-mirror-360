from django.db import transaction
from typing import Tuple
import logging

from django_skiptask.models import (
    Task,
    Queueable,
)


logger = logging.getLogger(__name__)


def enqueue_task(
    handler,
    payload=None,
    reattempts=0,
    run_timeout=None,
    queue_timeout=None,
    queue="default",
    key=None,
) -> Tuple[Queueable, Task]:
    if payload is None:
        payload = {}

    with transaction.atomic():
        task_dict = {
            "handler": handler.get_handler_key(),
            "payload": payload,
            "reattempts": reattempts,
        }
        if run_timeout:
            task_dict["run_timeout"] = run_timeout
        if queue_timeout:
            task_dict["queue_timeout"] = queue_timeout

        task = Task.objects.create(**task_dict)
        queueable = Queueable.objects.create(
            task=task,
            queue=queue,
            key=key,
            priority=100,
        )
        return queueable, task
