import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.pmb_core.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

try:
    User.objects.create_superuser(username, email, password)
    print(f'Superuser created successfully!\nUsername: {username}\nPassword: {password}')
except Exception as e:
    print(f'Error creating superuser: {str(e)}')
