from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from ...models import Bill

User = get_user_model()

class Command(BaseCommand):
    help = 'List all customers with their IDs and basic information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--search',
            type=str,
            help='Search term to filter customers by username, email, or ID',
            default=''
        )

    def handle(self, *args, **options):
        search_term = options['search'].lower()
        
        # Get all non-staff users (assuming customers are non-staff)
        customers = User.objects.filter(is_staff=False).order_by('id')
        
        if search_term:
            customers = customers.filter(
                Q(username__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(id__icontains=search_term)
            )
        
        if not customers.exists():
            self.stdout.write(self.style.WARNING('No customers found.'))
            return
        
        # Get bill counts for each customer
        customer_ids = customers.values_list('id', flat=True)
        bill_counts = dict(
            Bill.objects.filter(customer_id__in=customer_ids)
            .values_list('customer_id')
            .annotate(count=models.Count('id'))
        )
        
        # Prepare and display the customer list
        header = f"{'ID':<5} {'Username':<20} {'Email':<30} {'Date Joined':<20} {'Total Bills'}"
        self.stdout.write(self.style.MIGRATE_HEADING(header))
        self.stdout.write('-' * len(header))
        
        for customer in customers:
            bill_count = bill_counts.get(customer.id, 0)
            row = f"{customer.id:<5} {customer.username:<20} {customer.email[:28]:<30} {customer.date_joined.strftime('%Y-%m-%d'):<20} {bill_count}"
            self.stdout.write(row)
            
        self.stdout.write('\n' + self.style.SUCCESS(f'Found {customers.count()} customers'))
