from django.core.management.base import BaseCommand
from shipping.models import CityCode

class Command(BaseCommand):
    help = 'Initialize default city codes'

    def handle(self, *args, **options):
        # Default city codes (you can add more as needed)
        default_codes = [
            {'country': 'USA', 'postal_code': '10001', 'city': 'New York', 'state': 'NY'},
            {'country': 'USA', 'postal_code': '90001', 'city': 'Los Angeles', 'state': 'CA'},
            {'country': 'USA', 'postal_code': '60601', 'city': 'Chicago', 'state': 'IL'},
            {'country': 'USA', 'postal_code': '77001', 'city': 'Houston', 'state': 'TX'},
            {'country': 'USA', 'postal_code': '85001', 'city': 'Phoenix', 'state': 'AZ'},
            {'country': 'USA', 'postal_code': '19101', 'city': 'Philadelphia', 'state': 'PA'},
            {'country': 'USA', 'postal_code': '78201', 'city': 'San Antonio', 'state': 'TX'},
            {'country': 'USA', 'postal_code': '92101', 'city': 'San Diego', 'state': 'CA'},
            {'country': 'USA', 'postal_code': '75201', 'city': 'Dallas', 'state': 'TX'},
            {'country': 'USA', 'postal_code': '94101', 'city': 'San Francisco', 'state': 'CA'},
            {'country': 'USA', 'postal_code': '32801', 'city': 'Orlando', 'state': 'FL'},
            {'country': 'USA', 'postal_code': '33101', 'city': 'Miami', 'state': 'FL'},
        ]
        
        created_count = 0
        updated_count = 0
        
        for code_data in default_codes:
            city = code_data['city']
            postal_code = code_data['postal_code']
            state = code_data['state']
            country = code_data['country']
            
            # Check if this city code already exists
            existing_code = CityCode.objects.filter(
                city__iexact=city,
                postal_code=postal_code,
                state__iexact=state,
                country__iexact=country
            ).first()
            
            if existing_code:
                # Update existing code if needed
                if not existing_code.is_active:
                    existing_code.is_active = True
                    existing_code.save()
                    updated_count += 1
            else:
                # Create new city code
                CityCode.objects.create(
                    city=city,
                    state=state,
                    country=country,
                    postal_code=postal_code,
                    is_active=True
                )
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized city codes. Created: {created_count}, Updated: {updated_count}'
            )
        )
