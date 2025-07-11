from django.core.management.base import BaseCommand
from shipping.models import CourierPlan

class Command(BaseCommand):
    help = "Load courier plans data into DB"

    def handle(self, *args, **kwargs):
        courier_plans = [
            {
                "name": "UPS Shipping",
                "tagline": "Reliable & Progressive Value",
                "price_display": "₹2800+",
                "price_detail": "740/kg",
                "is_highlighted": True,
                "features": [
                    "Best for standard international shipping",
                    "Basic tracking included",
                    "Insurance available separately",
                    "Support for bulk consolidation",
                ],
                "cta": "Ship with UPS",
            },
            {
                "name": "DHL Shipping",
                "tagline": "Fast & Premium Delivery",
                "price_display": "₹3600+",
                "price_detail": "₹780/kg for above 5kgs",
                "is_highlighted": False,
                "features": [
                    "3–5 Day delivery",
                    "Includes advanced tracking",
                    "Priority handling",
                    "Reliable courier partner",
                ],
                "cta": "Ship with DHL",
            },
            {
                "name": "FedEx Shipping",
                "tagline": "Affordable & Consistent",
                "price_display": "₹2700+",
                "price_detail": "₹730/kg above 10 kg",
                "is_highlighted": False,
                "features": [
                    "5–7 Day delivery",
                    "Tracking included",
                    "Good for light to medium parcels",
                    "Trusted international service",
                ],
                "cta": "Ship with FedEx",
            },
        ]

        for plan in courier_plans:
            obj, created = CourierPlan.objects.update_or_create(
                name=plan["name"],
                defaults=plan
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated {obj.name}"))
