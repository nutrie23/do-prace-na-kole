# -*- coding: utf-8 -*-
# Generated by Django 1.9.5.dev20160531101208 on 2017-01-26 15:27
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('t_shirt_delivery', '0000_zero'),
        ('dpnk', '0050_move_models_to_t_shirt_delivery'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    state_operations = [
        migrations.CreateModel(
            name='DeliveryBatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Datum vytvoření')),
                ('customer_sheets', models.FileField(blank=True, null=True, upload_to='customer_sheets', verbose_name='Zákaznické listy')),
                ('tnt_order', models.FileField(blank=True, null=True, upload_to='tnt_order', verbose_name='Objednávka pro TNT')),
                ('dispatched', models.BooleanField(default=False, verbose_name='Vyřízeno')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deliverybatch_create', to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dpnk.Campaign', verbose_name='Kampaň')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deliverybatch_update', to=settings.AUTH_USER_MODEL, verbose_name='last updated by')),
            ],
            options={
                'db_table': 't_shirt_delivery_deliverybatch',
                'verbose_name': 'Dávka objednávek',
                'verbose_name_plural': 'Dávky objednávek',
            },
        ),
        migrations.CreateModel(
            name='PackageTransaction',
            fields=[
                ('transaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dpnk.Transaction')),
                ('tracking_number', models.PositiveIntegerField(unique=True, verbose_name='Tracking number TNT')),
                ('delivery_batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='t_shirt_delivery.DeliveryBatch', verbose_name='Dávka objednávek')),
            ],
            options={
                'db_table': 't_shirt_delivery_packagetransaction',
                'verbose_name': 'Transakce balíku',
                'verbose_name_plural': 'Transakce balíku',
            },
            bases=('dpnk.transaction',),
        ),
        migrations.AddField(
            model_name='packagetransaction',
            name='t_shirt_size',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='t_shirt_delivery.TShirtSize', verbose_name='Velikost trička'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
