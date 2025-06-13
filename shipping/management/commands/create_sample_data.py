from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shipping.models import ShippingAddress
from shipping.bill_models import Bill
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates sample shipping addresses and a bill'

    def handle(self, *args, **options):
        # Get or create a user
        User = get_user_model()
        user = User.objects.first()
        if not user:
            user = User.objects.create_user('sample_user', 'user@example.com', 'password')
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS('Created sample user'))

        # Create sample India address
        india_address = ShippingAddress.objects.create(
            user=user,
            address_line1='123 Tech Park',
            address_line2='Whitefield',
            city='Bangalore',
            state='Karnataka',
            country='India',
            postal_code='560066',
            phone_number='+91 9876543210',
            is_default=True
        )
        self.stdout.write(self.style.SUCCESS('Created India address'))

        # Create sample USA address
        usa_address = ShippingAddress.objects.create(
            user=user,
            address_line1='456 Silicon Valley',
            address_line2='Suite 1001',
            city='San Francisco',
            state='California',
            country='USA',
            postal_code='94025',
            phone_number='+1 555 123 4567',
            is_default=False
        )
        self.stdout.write(self.style.SUCCESS('Created USA address'))

        # Create a sample bill
        bill = Bill.objects.create(
            customer=user,
            created_by=user,
            amount=199.99,
            status='PENDING',
            due_date=timezone.now().date() + timezone.timedelta(days=30),
            description='Sample international shipping bill from India to USA'
        )
        self.stdout.write(self.style.SUCCESS(f'Created bill ID: {bill.id}'))
