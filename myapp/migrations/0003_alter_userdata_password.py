# Generated by Django 5.0.6 on 2024-10-07 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0002_alter_userdata_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userdata",
            name="password",
            field=models.CharField(max_length=256),
        ),
    ]
