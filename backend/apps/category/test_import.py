import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pmb_hello.settings')
django.setup()

# Now you can import your models
from shipping.models import Contact, ShippingAddress

def test_models():
    # Test creating a contact
    contact = Contact.objects.create(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone_number="1234567890"
    )
    print(f"Created contact: {contact}")
    
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
    print(f"Created address: {address}")

if __name__ == "__main__":
    test_models()
