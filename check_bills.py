import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.pmb_portal.pmb_portal.settings')
django.setup()

from django.utils import timezone
from shipping.bill_models import Bill

print("=== BILLING DATA CHECK ===")
today = timezone.now().date()
print(f"Current date (server): {today}")
print(f"Current time (server): {timezone.now()}")

# Count all bills
total_bills = Bill.objects.count()
print(f"\nTotal bills in database: {total_bills}")

# Show today's bills
todays_bills = Bill.objects.filter(created_at__date=today)
print(f"\nBills created today ({today}): {todays_bills.count()}")
for bill in todays_bills[:5]:  # Show first 5 for brevity
    print(f"  - ID: {bill.id}, Status: '{bill.status}', Amount: {bill.amount}, Created: {bill.created_at}")

# Show all unique statuses
statuses = Bill.objects.values_list('status', flat=True).distinct()
print("\nAll status values in database:", ", ".join(f"'{s}'" for s in statuses))

# Show recent bills (last 5)
print("\nMost recent bills:")
for bill in Bill.objects.order_by('-created_at')[:5]:
    print(f"  - ID: {bill.id}, Status: '{bill.status}', Amount: {bill.amount}, Created: {bill.created_at}")
