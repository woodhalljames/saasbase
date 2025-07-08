from django.db import migrations


def cleanup_user_image_favorites(apps, schema_editor):
    """Remove favorites that reference user_image since we only want processed_image favorites"""
    Favorite = apps.get_model('image_processing', 'Favorite')
    
    # Count how many user_image favorites exist
    user_image_favorites = Favorite.objects.filter(user_image__isnull=False)
    count = user_image_favorites.count()
    
    if count > 0:
        print(f"Removing {count} user_image favorites...")
        user_image_favorites.delete()
        print(f"Cleaned up {count} user_image favorites")
    else:
        print("No user_image favorites found to clean up")


def reverse_cleanup(apps, schema_editor):
    """This can't be reversed, but that's okay since we're cleaning up unwanted data"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('image_processing', '0002_generationpreset_remove_imageprocessingjob_cfg_scale_and_more'),  # Update this to your latest migration
    ]

    operations = [
        migrations.RunPython(cleanup_user_image_favorites, reverse_cleanup),
    ]