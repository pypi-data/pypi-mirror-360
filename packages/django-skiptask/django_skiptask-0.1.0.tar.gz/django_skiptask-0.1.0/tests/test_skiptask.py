from django_skiptask.models import (
    Queueable,
    AttemptStatusChoices,
    ResultStatusChoices,
)
from django_skiptask.tasks import ping, throw_exception, bad_sql, okay_sql, sleepy, sum
from django_skiptask.jobs import Sum
from django_skiptask.processing import process_tasks
from django_skiptask.handlers import enqueue_callable
import pytest


@pytest.mark.django_db(transaction=True)
def test_enqueue():
    enqueue_callable(ping)
    assert Queueable.objects.in_queue().count() == 1


@pytest.mark.django_db(transaction=True)
def test_dequeue():
    queueable, task = enqueue_callable(ping)
    assert Queueable.objects.in_queue().count() == 1
    process_tasks(stop_on_empty_queue=True)
    assert Queueable.objects.in_queue().count() == 0
    assert task.attempt_set.count() == 1
    assert task.attempt_set.first().status == AttemptStatusChoices.COMPLETED
    task.refresh_from_db()
    assert task.status == ResultStatusChoices.COMPLETED


@pytest.mark.django_db(transaction=True)
def test_result():
    queueable, task = enqueue_callable(sum, args=(2, 3))
    assert Queueable.objects.in_queue().count() == 1
    process_tasks(stop_on_empty_queue=True)
    assert Queueable.objects.in_queue().count() == 0
    assert task.attempt_set.count() == 1
    assert task.attempt_set.first().status == AttemptStatusChoices.COMPLETED
    assert task.attempt_set.first().value == 5
    task.refresh_from_db()
    assert task.status == ResultStatusChoices.COMPLETED
    assert Queueable.objects.filter(pk=queueable.pk).first() == None


@pytest.mark.django_db(transaction=True)
def test_job_result():
    queueable, task = Sum.enqueue(2, 3)
    assert Queueable.objects.in_queue().count() == 1
    process_tasks(stop_on_empty_queue=True)
    assert Queueable.objects.in_queue().count() == 0
    assert task.attempt_set.count() == 1
    assert task.attempt_set.first().status == AttemptStatusChoices.COMPLETED
    assert task.attempt_set.first().value == 5
    task.refresh_from_db()
    assert task.status == ResultStatusChoices.COMPLETED


@pytest.mark.django_db(transaction=True)
def test_dequeue_two():
    enqueue_callable(ping)
    enqueue_callable(ping)
    assert Queueable.objects.in_queue().count() == 2
    process_tasks(stop_on_empty_queue=True)
    assert Queueable.objects.in_queue().count() == 0


@pytest.mark.django_db(transaction=True)
def test_exception():
    queueable, task = enqueue_callable(throw_exception)
    process_tasks(stop_on_empty_queue=True)
    assert Queueable.objects.in_queue().count() == 0
    assert task.attempt_set.count() == 1
    assert task.attempt_set.first().status == AttemptStatusChoices.ERRORED


@pytest.mark.django_db(transaction=True)
def test_exception_reattempt():
    del throw_exception._count
    queueable, task = enqueue_callable(throw_exception, kwargs={"n": 3}, reattempts=2)
    process_tasks(stop_on_empty_queue=True)
    assert Queueable.objects.in_queue().count() == 0
    assert task.attempt_set.count() == 3
    assert (
        task.attempt_set.order_by("created_at").first().status
        == AttemptStatusChoices.ERRORED
    )
    assert (
        task.attempt_set.order_by("-created_at").first().status
        == AttemptStatusChoices.COMPLETED
    )


@pytest.mark.django_db(transaction=True)
def test_exception_reattempt_fail():
    queueable, task = enqueue_callable(throw_exception)
    process_tasks(stop_on_empty_queue=True)
    assert Queueable.objects.in_queue().count() == 0
    assert task.attempt_set.count() == 1
    assert task.attempt_set.first().status == AttemptStatusChoices.ERRORED
    task.refresh_from_db()
    assert task.status == ResultStatusChoices.ERRORED


@pytest.mark.django_db(transaction=True)
def test_db_transaction_isolation_fail():
    _, bad_task = enqueue_callable(bad_sql)
    _, okay_task = enqueue_callable(okay_sql)
    process_tasks(stop_on_empty_queue=True)
    assert Queueable.objects.in_queue().count() == 0
    # assert task.attempt_set.count() == 1
    assert all(
        [
            x.status == AttemptStatusChoices.ERRORED
            for x in bad_task.attempt_set.all()
        ]
    )
    assert all(
        [
            x.status == AttemptStatusChoices.COMPLETED
            for x in okay_task.attempt_set.all()
        ]
    )
    bad_task.refresh_from_db()
    assert bad_task.status == ResultStatusChoices.ERRORED


@pytest.mark.django_db(transaction=True)
def test_task_timeout():
    _, task = enqueue_callable(sleepy, run_timeout=5)
    process_tasks(stop_on_empty_queue=True)
    assert Queueable.objects.in_queue().count() == 0
    assert task.attempt_set.count() == 1
    assert task.attempt_set.first().status == AttemptStatusChoices.ERRORED
    task.refresh_from_db()
    assert task.status == ResultStatusChoices.ERRORED


# @pytest.mark.django_db()
# def test_processor_system():
#     worker = Worker(stop_on_empty_queue=True)
#     enqueue_callable(ping)
#     enqueue_callable(ping)
#     enqueue_callable(ping)
#     enqueue_callable(ping)
#     skiptask_processing.keep_processing = False
#     worker.start()
#     assert Attempt.objects.count() == 4
#     assert Queueable.objects.in_queue().count() == 0
