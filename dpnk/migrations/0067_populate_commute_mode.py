# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-12 10:48
from __future__ import unicode_literals

from django.db import migrations


def populate_commute_modes(apps, schema_editor):
    Trip = apps.get_model("dpnk", "Trip")
    CommuteMode = apps.get_model("dpnk", "CommuteMode")

    for commute_mode in CommuteMode.objects.all():
        print(commute_mode.slug)
        Trip.objects.filter(
            commute_mode=commute_mode.slug,
        ).update(
            commute_mode_choice=commute_mode,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0066_trip_commute_mode_choice'),
    ]

    operations = [
        migrations.RunPython(populate_commute_modes),
    ]
