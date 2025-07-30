from django.db import models, transaction
from functools import cached_property
import datetime
import json
import pytz

from .exceptions import NoQueueablesException


def utcnow():
    dt = datetime.datetime.now(pytz.utc)
    dt = dt.replace(tzinfo=pytz.utc)
    return dt


class TaskQuerySet(models.QuerySet):
    pass


RUN_TIMEOUT = 60 * 60  # 1 hour
QUEUE_TIMEOUT = 0


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()

        return super(DateTimeEncoder, self).default(obj)


class ResultStatusChoices(models.IntegerChoices):
    NEW = 0
    COMPLETED = 1
    ERRORED = 2


class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    handler = models.CharField(max_length=255)
    payload = models.JSONField(default=dict, encoder=DateTimeEncoder)
    reattempts = models.IntegerField(default=0)
    run_timeout = models.IntegerField(default=RUN_TIMEOUT)
    queue_timeout = models.IntegerField(default=QUEUE_TIMEOUT)
    created_at = models.DateTimeField(default=utcnow)
    status = models.IntegerField(
        choices=ResultStatusChoices.choices, default=ResultStatusChoices.NEW
    )
    objects = TaskQuerySet.as_manager()

    def __str__(self) -> str:
        name = f"{self.pk}"
        if args := self.payload.get("args"):
            name += f" args: {args}"
        if kwargs := self.payload.get("kwargs"):
            name += f" kwargs: {kwargs}"
        return name

    def __repr__(self) -> str:
        return f"<Task:{self.pk}>"

    def mark_complete(self):
        return Attempt.objects.create(task=self, status=AttemptStatusChoices.COMPLETED)

    def mark_error(self, message=""):
        return Attempt.objects.create(
            task=self, status=AttemptStatusChoices.ERRORED, message=message
        )

    @cached_property
    def last_attempt(self):
        return self.attempt_set.order_by("-created_at").first()


class QueueableQuerySet(models.QuerySet):
    def in_queue(self):
        return self.filter(in_queue=True)

    def in_process(self):
        return self.filter(in_queue=False)

    def get_queueable(self):
        if queueable := self.select_for_update(skip_locked=True).first():
            queueable.in_queue = False
            queueable.save()
            return queueable
        else:
            raise NoQueueablesException


class Queueable(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, primary_key=True)
    queue = models.SlugField(default="default")
    key = models.SlugField(unique=True, null=True)
    in_queue = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(default=100)
    objects = QueueableQuerySet.as_manager()

    def __str__(self) -> str:
        return self.task.__str__()

    def __repr__(self) -> str:
        return self.task.__repr__()


class AttemptStatusChoices(models.IntegerChoices):
    COMPLETED = 1
    ERRORED = 2


class Attempt(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=utcnow)
    status = models.IntegerField(choices=AttemptStatusChoices.choices)
    message = models.TextField(blank=True, default="")
    value = models.JSONField(null=True, encoder=DateTimeEncoder)
