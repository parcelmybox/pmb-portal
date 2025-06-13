import csv
from django.core.management.base import BaseCommand
from customerdetails.models import Customer

class Command(BaseCommand):
    help = 'Load customers from contacts.csv'

    def handle(self, *args, **kwargs):
        with open('contacts.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Customer.objects.get_or_create(
                    name=row['name'],
                    phone=row['phone'],
                    email=row['email']
                )
        self.stdout.write(self.style.SUCCESS('Customers loaded successfully.'))

