# Generated by Django 4.1.2 on 2022-10-31 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0007_auto_20221026_1052"),
    ]

    operations = [
        migrations.AddField(
            model_name="classroom",
            name="links",
            field=models.CharField(max_length=300, null=True),
        ),
    ]
