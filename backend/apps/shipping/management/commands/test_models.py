from django.core.management.base import BaseCommand
from shipping.models import Contact, ShippingAddress

class Command(BaseCommand):
    help = 'Test the Contact and ShippingAddress models'

    def handle(self, *args, **options):
        # Test creating a contact
        contact = Contact.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone_number="1234567890"
        )
        self.stdout.write(self.style.SUCCESS(f'Created contact: {contact}'))
        
        # Test creating a shipping address
        address = ShippingAddress.objects.create(
            contact=contact,
            address_line1="123 Test St",
            city="Test City",
            state="CA",
            country="USA",
            postal_code="12345",
            phone_number="1234567890",
            is_primary=True
        )
        self.stdout.write(self.style.SUCCESS(f'Created address: {address}'))
        
        # Verify the relationship
        self.stdout.write(f"Contact's addresses: {list(contact.shipping_addresses.all())}")
        self.stdout.write(f"Address's contact: {address.contact}")
