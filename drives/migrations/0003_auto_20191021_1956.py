# Generated by Django 2.2.5 on 2019-10-21 19:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drives', '0002_auto_20191020_2006'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driverreview',
            name='by',
        ),
        migrations.AddField(
            model_name='driverreview',
            name='by',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, related_name='driver_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='driverreview',
            name='of',
        ),
        migrations.AddField(
            model_name='driverreview',
            name='of',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, related_name='driver_of', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='riderreview',
            name='by',
        ),
        migrations.AddField(
            model_name='riderreview',
            name='by',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, related_name='rider_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='riderreview',
            name='of',
        ),
        migrations.AddField(
            model_name='riderreview',
            name='of',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, related_name='rider_of', to=settings.AUTH_USER_MODEL),
        ),
    ]
