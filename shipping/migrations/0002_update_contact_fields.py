from django.db import migrations, models
import django.core.validators
from django.core.validators import EmailValidator


def update_contacts(apps, schema_editor):
    Contact = apps.get_model('shipping', 'Contact')
    
    # Update existing contacts with default values
    for contact in Contact.objects.all():
        if not contact.first_name:
            contact.first_name = 'First'
        if not contact.last_name:
            contact.last_name = 'Last'
        if not contact.email:
            contact.email = f'user{contact.id}@example.com'  # Provide a unique email
        if not contact.phone_number:
            contact.phone_number = '0000000000'  # Default phone number
        if not contact.country:
            contact.country = 'USA'
        contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0001_initial'),
    ]

    operations = [
        # Make fields non-nullable with defaults
        migrations.AlterField(
            model_name='contact',
            name='first_name',
            field=models.CharField(default='', max_length=100, verbose_name='First Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contact',
            name='last_name',
            field=models.CharField(default='', max_length=100, verbose_name='Last Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(default='', max_length=254, unique=True, validators=[EmailValidator()], verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone_number',
            field=models.CharField(default='', max_length=20, verbose_name='Phone Number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contact',
            name='country',
            field=models.CharField(default='USA', max_length=100, verbose_name='Country'),
            preserve_default=False,
        ),
        migrations.RunPython(update_contacts, reverse_code=migrations.RunPython.noop),
    ]
