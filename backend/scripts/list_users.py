import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pmb_hello.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("\n{:<5} {:<20} {:<30} {:<20}".format("ID", "Username", "Email", "Date Joined"))
print("-" * 80)

for user in User.objects.all().order_by('id'):
    print("{:<5} {:<20} {:<30} {}".format(
        user.id,
        user.username[:18] + '..' if len(user.username) > 20 else user.username,
        (user.email or 'N/A')[:28],
        user.date_joined.strftime('%Y-%m-%d')
    ))

print()
