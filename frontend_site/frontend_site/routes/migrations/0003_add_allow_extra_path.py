# Generated by Django 3.0.9 on 2020-09-14 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0002_allow_empty_endpoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='allow_extra_path',
            field=models.BooleanField(default=False),
        ),
    ]