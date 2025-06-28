from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check and fix database timezone settings'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check current timezone
            cursor.execute("SELECT @@global.time_zone, @@session.time_zone")
            global_tz, session_tz = cursor.fetchone()
            
            self.stdout.write(f"Current timezone - Global: {global_tz}, Session: {session_tz}")
            
            # Try to set the timezone if needed
            try:
                cursor.execute("SET time_zone = 'America/Los_Angeles'")
                self.stdout.write(self.style.SUCCESS("Successfully set session timezone to 'America/Los_Angeles'"))
            except Exception as e:
                self.stderr.write(f"Error setting timezone: {e}")
                self.stdout.write("You may need to load timezone data into MySQL. Run these commands in MySQL:")
                self.stdout.write("  mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql")
                self.stdout.write("Then restart MySQL server.")
