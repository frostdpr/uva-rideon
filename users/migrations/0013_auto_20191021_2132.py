# Generated by Django 2.2.5 on 2019-10-21 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20191020_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_pic',
            field=models.ImageField(default='/media/default_profile_pic.jpg', upload_to='profile_pic/'),
        ),
    ]
