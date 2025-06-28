from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from shipping.models import Bill, Shipment
from shipping.activity import ActivityHistory

class Command(BaseCommand):
    help = 'Generate a bill for a customer or from a shipment'

    def add_arguments(self, parser):
        # Create mutually exclusive group for customer_id and shipment_id
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--customer-id', type=int, help='ID of the customer')
        group.add_argument('--shipment-id', type=int, help='ID of the shipment to bill')
        
        # Optional arguments
        parser.add_argument('--amount', type=float, help='Bill amount (optional for shipment)')
        parser.add_argument('--description', type=str, help='Bill description', default='')
        parser.add_argument('--payment-method', type=str, 
                          help='Payment method (e.g., CASH, CREDIT_CARD, BANK_TRANSFER)', 
                          default='CASH')
        parser.add_argument('--due-days', type=int, default=15,
                          help='Number of days until the bill is due (default: 15)')

    def handle(self, *args, **options):
        User = get_user_model()
        
        try:
            if options.get('shipment_id'):
                # Generate bill from shipment
                try:
                    shipment = Shipment.objects.get(id=options['shipment_id'])
                    bill = shipment.generate_bill(created_by=shipment.sender_address.user)
                    
                    # Update payment method if provided
                    if options.get('payment_method'):
                        bill.payment_method = options['payment_method']
                    
                    # Update due date if provided
                    if options.get('due_days'):
                        from django.utils import timezone
                        bill.due_date = timezone.now().date() + timezone.timedelta(days=options['due_days'])
                    
                    # Update description if provided
                    if options.get('description'):
                        bill.description = options['description']
                    
                    bill.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully created bill #{bill.id} for shipment {shipment.tracking_number}')
                    )
                except Shipment.DoesNotExist:
                    raise CommandError(f'Shipment with ID {options["shipment_id"]} does not exist')
                except Exception as e:
                    raise CommandError(f'Error generating bill from shipment: {str(e)}')
                
            else:  # Original manual bill creation
                try:
                    customer = User.objects.get(id=options['customer_id'])
                    
                    if not options.get('amount'):
                        raise CommandError('Amount is required when creating a manual bill')
                    
                    bill = Bill.objects.create(
                        customer=customer,
                        amount=options['amount'],
                        description=options['description'],
                        status='PENDING',
                        payment_method=options['payment_method'],
                        created_by=customer,
                        due_date=timezone.now().date() + timezone.timedelta(days=options['due_days'])
                    )
                    
                    # Log activity
                    ActivityHistory.objects.create(
                        user=customer,
                        action='Bill Generated',
                        content_object=bill,
                        details=f'Generated manual bill #{bill.id} for {customer.username}'
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully created bill #{bill.id} for {customer.username}')
                    )
                except User.DoesNotExist:
                    raise CommandError(f'Customer with ID {options["customer_id"]} does not exist')
                
        except Exception as e:
            raise CommandError(str(e))
