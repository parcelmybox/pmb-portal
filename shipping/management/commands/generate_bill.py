from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shipping.bill_models import Bill
from shipping.activity import ActivityHistory

class Command(BaseCommand):
    help = 'Generate a bill for a customer'

    def add_arguments(self, parser):
        parser.add_argument('customer_id', type=int, help='ID of the customer')
        parser.add_argument('amount', type=float, help='Bill amount')
        parser.add_argument('--description', type=str, help='Bill description', default='')
        parser.add_argument('--payment-method', type=str, help='Payment method (e.g., CASH, CREDIT_CARD, BANK_TRANSFER)', default='CASH')

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            customer = User.objects.get(id=options['customer_id'])
            bill = Bill.objects.create(
                customer=customer,
                amount=options['amount'],
                description=options['description'],
                status='PENDING',
                payment_method=options['payment_method'],
                created_by=customer
            )
            
            # Log activity
            ActivityHistory.objects.create(
                user=customer,
                action='Bill Generated',
                content_object=bill
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created bill #{bill.id} for {customer.username}')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Customer with ID {options["customer_id"]} does not exist')
            )
