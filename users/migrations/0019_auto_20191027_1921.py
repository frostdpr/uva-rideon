# Generated by Django 2.2.5 on 2019-10-27 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20191022_0331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='about',
            field=models.TextField(default='Write a bio to let people know about you!', max_length=1000),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='gender',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='name',
            field=models.CharField(default='', max_length=50),
        ),
    ]
