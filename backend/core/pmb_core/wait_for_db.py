"""
Utility to wait for database to be available before starting Django.
"""
import time
import sys
from django.db import connections
from django.db.utils import OperationalError


def wait_for_db():
    """Wait for database to be available."""
    max_retries = 30
    retry_delay = 2  # seconds

    for i in range(max_retries):
        try:
            # Try to connect to the database
            db_conn = connections['default']
            db_conn.ensure_connection()
            print("\nDatabase is available!")
            return True
        except OperationalError as e:
            if i == max_retries - 1:
                print(f"\nError: Could not connect to database after {max_retries} attempts.")
                print(f"Error details: {str(e)}")
                return False
            print(f"Waiting for database... (Attempt {i + 1}/{max_retries})")
            time.sleep(retry_delay)


if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pmb_hello.settings')
    django.setup()
    
    if not wait_for_db():
        sys.exit(1)
