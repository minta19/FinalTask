# Generated by Django 4.2.4 on 2023-08-17 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='Ordered_price',
        ),
        migrations.RemoveField(
            model_name='order',
            name='Ordered_quantity',
        ),
    ]
