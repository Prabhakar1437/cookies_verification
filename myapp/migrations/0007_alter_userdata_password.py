# Generated by Django 5.0.6 on 2024-10-10 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0006_remove_userdata_crypto_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userdata",
            name="password",
            field=models.CharField(max_length=256),
        ),
    ]