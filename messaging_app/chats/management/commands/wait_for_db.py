# chats/management/commands/wait_for_db.py

import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for database to be available"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        max_retries = 10
        retry_delay = 5  # seconds

        for _ in range(max_retries):
            try:
                db_conn = connections["default"]
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS("Database available!"))
                return
            except OperationalError:
                self.stdout.write("Database unavailable, waiting...")
                time.sleep(retry_delay)

        self.stdout.write(self.style.ERROR("Database not available after waiting!"))
        exit(1)
