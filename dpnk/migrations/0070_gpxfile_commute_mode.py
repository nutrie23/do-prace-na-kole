# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-12 12:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0069_auto_20170512_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpxfile',
            name='commute_mode_choice',
            field=models.ForeignKey(default=1, on_delete=models.deletion.CASCADE, to='dpnk.CommuteMode', verbose_name='Mód dopravy'),
        ),
    ]
