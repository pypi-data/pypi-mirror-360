from django.core.management.base import BaseCommand
from django.utils import autoreload
import signal

from django_skiptask.commands import exit_gracefully
from django_skiptask.worker import Worker


class Command(BaseCommand):
    help = "Starts a worker to process the queue with auto reload"

    def handle(self, *args, **options):
        signal.signal(signal.SIGINT, exit_gracefully)
        worker = Worker()
        autoreload.run_with_reloader(worker.start)
