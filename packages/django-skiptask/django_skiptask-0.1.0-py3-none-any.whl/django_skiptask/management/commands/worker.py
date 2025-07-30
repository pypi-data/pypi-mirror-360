from django.core.management.base import BaseCommand
import signal

from django_skiptask.commands import exit_gracefully
from django_skiptask.worker import Worker


class Command(BaseCommand):
    help = "Starts a worker to process the queue"

    def handle(self, *args, **options):
        signal.signal(signal.SIGINT, exit_gracefully)
        worker = Worker()
        worker.start()
