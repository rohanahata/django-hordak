# Generated by Django 5.1b1 on 2024-07-01 06:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("hordak", "0052_amount_to_debit_credit_sql"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="leg",
            name="amount",
        ),
        migrations.RemoveField(
            model_name="leg",
            name="amount_currency",
        ),
    ]
