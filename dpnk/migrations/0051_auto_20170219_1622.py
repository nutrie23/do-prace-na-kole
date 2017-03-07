# -*- coding: utf-8 -*-
# Generated by Django 1.9.5.dev20160531101208 on 2017-02-19 16:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0050_move_models_to_t_shirt_delivery'),
        ('t_shirt_delivery', '0002_auto_20170130_0343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userattendance',
            name='t_shirt_size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='t_shirt_delivery.TShirtSize', verbose_name='Velikost trička'),
        ),
    ]