# Generated by Django 4.0.3 on 2022-03-08 20:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0002_input_rename_todolist_collection_delete_item_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='collection', to=settings.AUTH_USER_MODEL),
        ),
    ]
