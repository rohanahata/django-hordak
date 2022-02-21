# Generated by Django 2.2.3 on 2019-07-23 09:29

import djmoney.models.fields
from django.db import migrations, models

from hordak.defaults import DECIMAL_PLACES, MAX_DIGITS


class Migration(migrations.Migration):

    dependencies = [
        ("hordak", "0025_auto_20180829_1605"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="level",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="account",
            name="lft",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="account",
            name="rght",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="leg",
            name="amount",
            field=djmoney.models.fields.MoneyField(
                decimal_places=DECIMAL_PLACES,
                max_digits=MAX_DIGITS,
                default_currency="EUR",
                help_text="Record debits as positive, credits as negative",
            ),
        ),
    ]
