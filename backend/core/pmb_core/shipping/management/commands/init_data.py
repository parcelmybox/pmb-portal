from django.core.management.base import BaseCommand
from shipping.models import ShippingRate

class Command(BaseCommand):
    help = 'Initialize shipping rates'

    def handle(self, *args, **options):
        # Add some sample shipping rates
        rates = [
            {'weight_range_start': 0, 'weight_range_end': 1, 'price': 5.00},
            {'weight_range_start': 1, 'weight_range_end': 5, 'price': 10.00},
            {'weight_range_start': 5, 'weight_range_end': 10, 'price': 15.00},
            {'weight_range_start': 10, 'weight_range_end': 20, 'price': 25.00},
            {'weight_range_start': 20, 'weight_range_end': 50, 'price': 40.00},
        ]

        for rate in rates:
            ShippingRate.objects.create(
                weight_range_start=rate['weight_range_start'],
                weight_range_end=rate['weight_range_end'],
                price=rate['price']
            )

        self.stdout.write(self.style.SUCCESS('Successfully initialized shipping rates'))
