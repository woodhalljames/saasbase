from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('wedding_shopping', '0004_alter_socialmedialink_platform'),
    ]

    operations = [
        # Just rename the URL field first
        migrations.RenameField(
            model_name='registrylink',
            old_name='original_url',
            new_name='url',
        ),
    ]
