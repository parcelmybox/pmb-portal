import time
import os
import MySQLdb
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    """Django command to pause execution until database is available"""
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Maximum number of seconds to wait for the database',
        )

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        max_retries = options['timeout']
        retry_count = 0
        
        db_config = {
            'host': os.getenv('DB_HOST', 'db'),
            'user': os.getenv('DB_USER', 'pmb_user'),
            'password': os.getenv('DB_PASSWORD', 'pmb_user'),
            'database': os.getenv('DB_NAME', 'pmb_db'),
            'port': int(os.getenv('DB_PORT', 3306)),
        }

        while retry_count < max_retries:
            try:
                # Try to connect directly to MySQL
                conn = MySQLdb.connect(**db_config)
                conn.ping(True)  # Check if the connection is alive
                conn.close()
                
                # Also check Django's connection
                db_conn = connections['default']
                db_conn.ensure_connection()
                
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
                
            except (OperationalError, MySQLdb.OperationalError) as e:
                if retry_count == 0:
                    self.stdout.write(f'Database connection error: {str(e)}')
                self.stdout.write(f'Waiting for database... (attempt {retry_count + 1}/{max_retries})')
                time.sleep(1)
                retry_count += 1
        
        self.stdout.write(self.style.ERROR('Could not connect to database after multiple attempts'))
        raise Exception('Database connection failed')
