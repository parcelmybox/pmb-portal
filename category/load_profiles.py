import csv
import os
import re
import sys
import difflib
from datetime import datetime
from django.core.validators import validate_email, ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from typing import Dict, List, Tuple, Optional
from shipping.models import Contact, ShippingAddress

ZIP_CODE_MAPPINGS = {
    'RI': '95330',
    'MANTECA': '95336',
    'SAN JOSE': '95134',
    'SUNNYVALE': '94085',
    'FREMONT': '94538',
    'SAN FRANCISCO': '94105',
}

def parse_name(full_name):
    if not full_name:
        return '', ''
    parts = full_name.strip().split()
    if not parts:
        return '', ''
    if len(parts) == 1:
        return parts[0], ''
    return ' '.join(parts[:-1]), parts[-1]

def import_contacts(filename):
    """Import contacts from CSV file with improved error handling and duplicate detection"""
    if not os.path.exists(filename):
        print(f"❌ Error: File not found: {filename}")
        return

    stats = {
        'total': 0,
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': []
    }

    try:
        with open(filename, 'r', encoding='utf-8-sig') as csvfile:
            # Try to detect the CSV dialect
            try:
                sample = csvfile.read(1024)
                csvfile.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                csvfile.seek(0)
                reader = csv.DictReader(csvfile, dialect=dialect)
            except:
                # Fallback to default CSV format if sniffing fails
                csvfile.seek(0)
                reader = csv.DictReader(csvfile)

            with transaction.atomic():
                for row_num, row in enumerate(reader, 1):
                    try:
                        stats['total'] += 1
                        
                        # Normalize field names (case insensitive)
                        row = {k.strip().lower(): v for k, v in row.items() if k}
                        
                        # Extract and clean data
                        full_name = row.get('name', '').strip()
                        email = (row.get('email', '') or row.get('e-mail', '') or '').strip().lower()
                        phone = clean_phone(row.get('phone', '') or row.get('phone 1 - value', ''))
                        address = (row.get('address', '') or row.get('address 1 - formatted', '')).strip()
                        
                        # Skip if missing required fields
                        if not (full_name or email):
                            stats['skipped'] += 1
                            stats['errors'].append(f"Row {row_num}: Missing both name and email")
                            continue
                            
                        # Parse name
                        first_name, last_name = parse_name(full_name)
                        
                        # Check for existing contact by email or phone
                        existing = None
                        if email:
                            existing = CustomerProfile.objects.filter(email__iexact=email).first()
                        if not existing and phone:
                            existing = CustomerProfile.objects.filter(phone=phone).first()
                        
                        # Create or update contact
                        if existing:
                            # Update existing contact
                            update_fields = {}
                            if first_name and not existing.first_name:
                                update_fields['first_name'] = first_name
                            if last_name and not existing.last_name:
                                update_fields['last_name'] = last_name
                            if email and not existing.email:
                                update_fields['email'] = email
                            if phone and not existing.phone:
                                update_fields['phone'] = phone
                            
                            if update_fields:
                                for field, value in update_fields.items():
                                    setattr(existing, field, value)
                                existing.save()
                                stats['updated'] += 1
                                print(f"🔄 Updated: {existing}")
                            else:
                                stats['skipped'] += 1
                                print(f"⏭️  Exists (no changes): {existing}")
                        else:
                            # Create new contact
                            contact = CustomerProfile(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone=phone,
                                address=address
                            )
                            contact.save()
                            stats['created'] += 1
                            print(f"✅ Created: {contact}")
                            
                            # Create shipping address if address data exists
                            if address:
                                try:
                                    shipping_address = ShippingAddress(
                                        address_line1=address[:255],  # Truncate to max_length
                                        city=row.get('city', ''),
                                        state=row.get('state', ''),
                                        country=row.get('country', 'USA'),
                                        postal_code=row.get('zip', row.get('postal_code', '')),
                                        phone_number=phone
                                    )
                                    shipping_address.save()
                                    print(f"  📫 Added shipping address: {shipping_address}")
                                except Exception as e:
                                    stats['errors'].append(f"Row {row_num}: Error creating shipping address - {str(e)}")
                                    print(f"  ⚠️  Warning: Could not create shipping address - {str(e)}")
                        
                    except Exception as e:
                        error_msg = f"Row {row_num}: {str(e)}"
                        stats['errors'].append(error_msg)
                        print(f"❌ {error_msg}")
                        continue

    except Exception as e:
        stats['errors'].append(f"Fatal error: {str(e)}")
        print(f"❌ Fatal error: {str(e)}")
    
    # Print summary
    print("\n" + "="*50)
    print("IMPORT SUMMARY")
    print("="*50)
    print(f"Total rows processed: {stats['total']}")
    print(f"Contacts created: {stats['created']}")
    print(f"Contacts updated: {stats['updated']}")
    print(f"Rows skipped: {stats['skipped']}")
    
    if stats['errors']:
        print("\nErrors encountered:")
        for error in stats['errors'][:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more errors")

if __name__ == "__main__":
    # Use the path from your existing code
    filename = r"C:\Users\mural\OneDrive\Desktop\Parcelmybox\contacts-pmb.csv"
    import_contacts(filename)