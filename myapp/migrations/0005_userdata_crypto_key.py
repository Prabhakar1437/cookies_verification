# Generated by Django 5.0.6 on 2024-10-07 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0004_alter_userdata_password"),
    ]

    operations = [
        migrations.AddField(
            model_name="userdata",
            name="crypto_key",
            field=models.CharField(default=None, max_length=400, null=True),
        ),
    ]
