from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from ...models import Bill, ActivityHistory

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate a bill for a customer'

    def add_arguments(self, parser):
        parser.add_argument('customer_id', type=int, help='ID of the customer')
        parser.add_argument('amount', type=float, help='Amount for the bill')
        parser.add_argument('--description', type=str, default='', help='Description for the bill')

    def handle(self, *args, **options):
        customer_id = options['customer_id']
        amount = options['amount']
        description = options['description']

        try:
            # Get the customer
            customer = User.objects.get(id=customer_id)
            
            # Create the bill
            bill = Bill.objects.create(
                customer=customer,
                amount=amount,
                description=description,
                status='PENDING'
            )
            
            # Log the activity
            ActivityHistory.objects.create(
                user=customer,
                activity_type='BILL_GENERATED',
                description=f'Generated bill #{bill.id} for {customer.username} - ${amount:.2f}',
                reference_id=bill.id,
                reference_model='Bill'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created bill #{bill.id} for {customer.username} - ${amount:.2f}'
                )
            )
            
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Customer with ID {customer_id} does not exist'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error generating bill: {str(e)}'))
