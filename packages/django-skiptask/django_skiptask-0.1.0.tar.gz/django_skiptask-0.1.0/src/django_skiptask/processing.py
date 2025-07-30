from django.db import transaction
from time import sleep
from typing import Tuple, Type
import logging

from .models import (
    Queueable,
    Attempt,
    AttemptStatusChoices,
    ResultStatusChoices,
)

from .exceptions import NoQueueablesException
from .handlers import registry


logger = logging.getLogger(__name__)
keep_processing = True


def process_queueable(queueable):
    task = queueable.task
    logger.info(f"Starting task {task.pk}")

    handler_cls = registry.get(task.handler)
    if not handler_cls:
        raise RuntimeError("No handler found")
    handler = handler_cls()

    try:
        value = handler.handle(task)
        attempt_status = AttemptStatusChoices.COMPLETED
        result_status = ResultStatusChoices.COMPLETED
    except Exception as e:
        logger.info(e)
        value = None
        attempt_status = AttemptStatusChoices.ERRORED
        result_status = ResultStatusChoices.ERRORED
    finally:
        attempt = Attempt.objects.create(task=task, status=attempt_status, value=value)

    task.status = result_status
    task.save()

    if attempt.status == AttemptStatusChoices.COMPLETED:
        logger.info(f"Task {task.pk} completed with attempt {attempt.pk}")
        queueable.delete()
    else:
        logger.info(f"Task {task.pk} failed with attempt {attempt.pk}")
        # Add one to reattempts to count the original attempt
        if task.attempt_set.count() < task.reattempts + 1:
            logger.info(f"Task {task.pk} requeueing")
            queueable.in_queue = True
            queueable.save()


class Processor:
    qs = None
    queue = "default"
    sleep = 2

    def __init__(self, qs=None, stop_on_empty_queue: bool = True) -> None:
        if self.qs is None:
            self.qs = Queueable.objects.filter(queue=self.queue).in_queue()
            self.stop_on_empty_queue = stop_on_empty_queue

    def get_queueable(self):
        with transaction.atomic(durable=True):
            logger.info(f"Checking for queueable")
            queueable = self.qs.get_queueable()
        return queueable

    def process_queueable(self):
        queueable = self.get_queueable()
        process_queueable(queueable)

    def get_sleep(self):
        return self.sleep

    def keep_processing(self):
        return keep_processing

    def process(self):
        while self.keep_processing():
            queueables = True
            try:
                self.process_queueable()
            except NoQueueablesException:
                queueables = False
            if self.stop_on_empty_queue and not queueables:
                return
            elif not queueables:
                # A lil pause before trying to get the next item
                sleep(self.get_sleep())


def process_tasks(
    processor_class: Type[Processor] = Processor, stop_on_empty_queue: bool = True
):
    processor = processor_class(stop_on_empty_queue=stop_on_empty_queue)
    processor.process()
