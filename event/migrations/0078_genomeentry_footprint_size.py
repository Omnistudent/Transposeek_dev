# Generated by Django 4.2 on 2024-07-19 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0077_remove_genomeentry_footprint_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='genomeentry',
            name='footprint_size',
            field=models.IntegerField(default=-1, verbose_name='footprint_size'),
        ),
    ]
