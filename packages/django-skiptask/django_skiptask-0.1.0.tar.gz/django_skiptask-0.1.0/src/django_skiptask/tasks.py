from time import sleep
from .models import Attempt


def ping():
    print("ping")


def throw_exception(n=None):
    if hasattr(throw_exception, "_count"):
        throw_exception._count += 1
    else:
        throw_exception._count = 1

    print(throw_exception._count)
    if throw_exception._count == n:
        return None
    raise Exception("This is busted.")


def bad_sql():
    bad_query = Attempt.objects.raw("DELETE FART FROM 12")
    for row in bad_query:
        print(row)


def okay_sql():
    attempt = Attempt.objects.first()
    return True


def sum(x, y):
    print(x + y)
    return x + y


def say(text=None):
    print(text)


def sumsay(x, y, text):
    print(f"{x} + {y} is {text}")


def sleepy():
    sleep(10)
