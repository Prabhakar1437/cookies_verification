# Generated by Django 5.0.6 on 2024-10-07 16:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0005_userdata_crypto_key"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userdata",
            name="crypto_key",
        ),
    ]
