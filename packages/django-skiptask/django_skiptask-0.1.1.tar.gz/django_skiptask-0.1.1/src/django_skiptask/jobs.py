from .handlers import enqueue_callable


class Job:
    @classmethod
    def setup(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        return obj

    @classmethod
    def process(cls, *args, **kwargs):
        obj = cls.setup(*args, **kwargs)
        result = obj.run()
        return result

    @classmethod
    def enqueue(cls, *args, **kwargs):
        queueable, task = enqueue_callable(cls.process, args=args, kwargs=kwargs)
        return queueable, task

    def run(self):
        # The main body of the task
        pass


class Sum(Job):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def run(self):
        return self.x + self.y
