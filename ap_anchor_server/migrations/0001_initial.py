# Generated by Django 4.0.6 on 2022-07-30 16:17

import ap_anchor_server.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.PositiveBigIntegerField(
                        default=ap_anchor_server.models.positive_big_integer,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("first_name", models.CharField(max_length=128)),
                ("last_name", models.CharField(max_length=128)),
                ("bank_account_number", models.CharField(max_length=128)),
                ("bank_number", models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="StellarId",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("account", models.CharField(max_length=128)),
                ("memo", models.CharField(max_length=128)),
                ("memo_type", models.CharField(max_length=4)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ap_anchor_server.customer",
                    ),
                ),
            ],
        ),
    ]
