# -*- coding: utf-8 -*-
# Generated by Django 1.9.5.dev20160531101208 on 2016-06-07 11:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0032_competition_show_results'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='points_given',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]
