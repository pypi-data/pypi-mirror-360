import django
import multiprocessing
from typing import Callable

from .processing import process_tasks


class Worker:
    def __init__(
        self,
        process_tasks: Callable = process_tasks,
        n_worker_processes: int = 4,
        stop_on_empty_queue: bool = False,
    ) -> None:
        self._process_tasks = process_tasks
        self.n_worker_processes = n_worker_processes
        self.stop_on_empty_queue = stop_on_empty_queue
        self._process_results = []

    def _start_worker_process(self, pool):
        async_result = pool.apply_async(
            self._process_tasks, kwds={"stop_on_empty_queue": self.stop_on_empty_queue}
        )
        return async_result

    def start(self):
        with multiprocessing.Pool(self.n_worker_processes, maxtasksperchild=1, initializer=django.setup) as pool:
            process_results = []
            for i in range(self.n_worker_processes):
                async_result = self._start_worker_process(pool)
                process_results.append(async_result)
            while True:
                for result in process_results:
                    # If a process is done (no matter the reason), maybe start a new one to take its place.
                    if result.ready():
                        process_results.remove(result)
                        # If processing should be done don't launch any more and let things finish up naturally.
                        from django_skiptask import processing

                        if processing.keep_processing:
                            async_result = self._start_worker_process(pool)
                            process_results.append(async_result)
                if not process_results:
                    break

    def stop(self):
        from django_skiptask import processing

        # global keep_processing
        processing.keep_processing = False
