# Generated by Django 2.1.3 on 2019-10-14 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drives', '0002_auto_20191013_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drive',
            name='date_time',
            field=models.DateTimeField(),
        ),
    ]
