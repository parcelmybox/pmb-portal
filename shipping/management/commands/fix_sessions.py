from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
import os

class Command(BaseCommand):
    help = 'Fix session issues by clearing all sessions and ensuring the sessions table exists'

    def handle(self, *args, **options):
        # Ensure the sessions table exists
        try:
            # This will create the sessions table if it doesn't exist
            Session.objects.exists()
            self.stdout.write(self.style.SUCCESS('Sessions table exists'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error accessing sessions table: {e}'))
            self.stdout.write('Running migrations to ensure sessions table exists...')
            os.system('python manage.py migrate sessions')
        
        # Clear all sessions
        try:
            count = Session.objects.count()
            Session.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Cleared {count} sessions'))
            
            # Create a new session to ensure everything is working
            session = SessionStore()
            session.create()
            self.stdout.write(self.style.SUCCESS('Successfully created a new session'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error clearing sessions: {e}'))
            self.stdout.write('Try running migrations: python manage.py migrate')
            
        self.stdout.write('\nPlease restart your development server for changes to take effect.')
