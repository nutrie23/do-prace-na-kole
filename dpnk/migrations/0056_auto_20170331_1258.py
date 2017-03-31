# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-31 12:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0055_auto_20170329_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='package_max_count',
            field=models.PositiveIntegerField(blank=True, default=50, null=True, verbose_name='Maximální počet triček v krabici'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Doména v URL'),
        ),
    ]
