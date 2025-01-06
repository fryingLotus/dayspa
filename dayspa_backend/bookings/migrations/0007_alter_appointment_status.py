# Generated by Django 5.1.3 on 2024-11-27 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0006_appointment_coupon"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="status",
            field=models.CharField(
                choices=[
                    ("confirmed", "Confirmed"),
                    ("pending", "Pending"),
                    ("canceled", "Canceled"),
                    ("completed", "Completed"),
                ],
                max_length=50,
            ),
        ),
    ]