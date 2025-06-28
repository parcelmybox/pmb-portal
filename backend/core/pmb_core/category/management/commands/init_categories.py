from django.core.management.base import BaseCommand
from apps.category.models import Category

class Command(BaseCommand):
    help = 'Initialize sample categories'

    def handle(self, *args, **options):
        # Add some sample categories
        categories = [
            {
                'name': 'Electronics',
                'description': 'Electronics and gadgets'
            },
            {
                'name': 'Clothing',
                'description': 'Apparel and accessories'
            },
            {
                'name': 'Books',
                'description': 'Books and educational materials'
            },
            {
                'name': 'Food',
                'description': 'Food items and groceries'
            },
            {
                'name': 'Furniture',
                'description': 'Home furniture and decor'
            }
        ]

        for category in categories:
            Category.objects.create(
                name=category['name'],
                description=category['description']
            )

        self.stdout.write(self.style.SUCCESS('Successfully initialized categories'))
