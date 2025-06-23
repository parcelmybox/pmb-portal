from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check the database schema for the shipping_shipment table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM shipping_shipment")
            columns = cursor.fetchall()
            self.stdout.write("Columns in shipping_shipment table:")
            for column in columns:
                self.stdout.write(f"- {column[0]} ({column[1]})")
