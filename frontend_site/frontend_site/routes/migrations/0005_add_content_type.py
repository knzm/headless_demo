# Generated by Django 3.0.10 on 2020-09-14 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0004_allow_empty_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='content_type',
            field=models.TextField(default='text/html'),
        ),
    ]