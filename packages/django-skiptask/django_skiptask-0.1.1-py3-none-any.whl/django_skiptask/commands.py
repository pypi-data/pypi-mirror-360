from django.core.management.base import BaseCommand
from time import sleep
import logging
import signal
import sys

from django_skiptask import processing
from django_skiptask.processing import process_tasks

logger = logging.getLogger(__name__)
sigint_happened = False


def exit_gracefully(signum, frame):
    global sigint_happened

    if sigint_happened == True:
        logger.info("Hard exit.")
        sys.exit(1)
    else:
        logger.info("Soft exit. Finishing up current task, then ending.")

    sigint_happened = True
    processing.keep_processing = False

    signal.signal(signal.SIGINT, exit_gracefully)


class SkipTaskCommand(BaseCommand):
    help = 'Starts a worker to process the queue with auto reload'

    def handle(self, *args, **options):
        signal.signal(signal.SIGINT, exit_gracefully)
