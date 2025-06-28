from django.core.management.base import BaseCommand
from django.core.management import get_commands

class Command(BaseCommand):
    help = 'List all available management commands'

    def handle(self, *args, **options):
        commands = get_commands()
        self.stdout.write("Available commands:")
        for name, path in sorted(commands.items()):
            self.stdout.write(f"  {name}: {path}")
