# Generated by Django 3.0.9 on 2020-09-14 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0003_add_allow_extra_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='path',
            field=models.TextField(blank=True),
        ),
    ]
