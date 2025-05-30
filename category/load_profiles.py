import django
import os
import csv
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pmb_hello.settings')
django.setup()

from category.models import CustomerProfile


class Profile:
    def __init__(self, name, email, phone, address):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address

    def __repr__(self):
        return f"Profile(name='{self.name}', email='{self.email}', phone='{self.phone}', address='{self.address}')"

def load_profiles(csv_filename):
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        print(f"🔍 CSV Columns Detected: {reader.fieldnames}")
        for row in reader:
            full_name = f"{row.get('First Name', '').strip()} {row.get('Last Name', '').strip()}".strip()
            email = row.get('E-mail 1 - Value', '').strip()
            phone = row.get('Phone 1 - Value', '').strip()
            address = row.get('Address 1 - Formatted', '').strip()

            # Avoid duplicates
            if full_name:
                obj, created = CustomerProfile.objects.get_or_create(
                    name=full_name,
                    email=email,
                    phone=phone,
                    address=address
                )
                print(f"{'✅ Created' if created else '🔁 Exists'}: {obj}")


if __name__ == "__main__":
    filename = r"C:\Users\mural\OneDrive\Desktop\Parcelmybox\contacts-pmb.csv"
    load_profiles(filename)
