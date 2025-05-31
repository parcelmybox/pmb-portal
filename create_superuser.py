import os
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
