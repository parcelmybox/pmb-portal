from django.core.management.base import BaseCommand
from django.db import connection
import subprocess
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Load timezone data into MySQL'

    def handle(self, *args, **options):
        # Get MySQL executable path (assuming it's in the system PATH)
        mysql_path = 'mysql'
        
        # Get database settings
        db_settings = connection.settings_dict
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings['HOST']
        db_port = db_settings['PORT'] or '3306'
        
        # Build the command to load timezone data
        cmd = [
            'mysql_tzinfo_to_sql',
            '/usr/share/zoneinfo',
            '|',
            'mysql',
            f'--host={db_host}',
            f'--port={db_port}',
            f'--user={db_user}',
            f'--password={db_password}',
            'mysql'
        ]
        
        self.stdout.write(self.style.WARNING("This command requires root access to MySQL."))
        self.stdout.write("Run this command with sudo:")
        self.stdout.write(self.style.SUCCESS(' '.join(cmd)))
        
        # Alternative: Direct SQL to set timezone
        self.stdout.write("\nOr run these SQL commands in your MySQL client:")
        self.stdout.write(self.style.SQL_KEYWORD("SET GLOBAL time_zone = 'America/Los_Angeles';"))
        self.stdout.write(self.style.SQL_KEYWORD("SET time_zone = 'America/Los_Angeles';"))
        self.stdout.write(self.style.SQL_KEYWORD("SET GLOBAL time_zone = '-08:00';"))
        self.stdout.write(self.style.SQL_KEYWORD("SET time_zone = '-08:00';") + "\n")
        
        self.stdout.write(self.style.SUCCESS("After running the above, add this to your Django settings.py:"))
        self.stdout.write("""
# settings.py
USE_TZ = True
TIME_ZONE = 'America/Los_Angeles'
""")
