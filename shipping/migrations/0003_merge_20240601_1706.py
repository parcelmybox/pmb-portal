from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0002_citycode'),
        ('shipping', '0002_update_contact_fields'),
    ]

    operations = [
        # This is an empty migration that just depends on the conflicting migrations
    ]
