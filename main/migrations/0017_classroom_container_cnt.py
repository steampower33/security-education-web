# Generated by Django 4.1.2 on 2022-11-28 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0016_remove_classroom_container_cnt"),
    ]

    operations = [
        migrations.AddField(
            model_name="classroom",
            name="container_cnt",
            field=models.IntegerField(default=0),
        ),
    ]