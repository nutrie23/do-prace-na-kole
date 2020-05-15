# Generated by Django 2.2.11 on 2020-05-02 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motivation_messages', '0003_auto_20200501_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='motivationmessage',
            name='day_from',
            field=models.IntegerField(blank=True, help_text='Počet dní od začátku soutěžní fáze kampaně. Možno zadat i záporné hodnoty pro období před kampaní.', null=True, verbose_name='Ode dne'),
        ),
        migrations.AlterField(
            model_name='motivationmessage',
            name='day_to',
            field=models.IntegerField(blank=True, help_text='Počet dní od začátku soutěžní fáze kampaně. Možno zadat i záporné hodnoty pro období před kampaní.', null=True, verbose_name='Do dne'),
        ),
        migrations.AlterField(
            model_name='motivationmessage',
            name='priority',
            field=models.IntegerField(default=0, help_text='Priorita hlášky. Zobrazuje se vždy náhodná hláška z těch, které mají nejvyšší prioritu splňují ostatní podmínky.Možno nastavit záporě pro hlášky které mají mít zobrazovat jen pokud není žádní lepší k dispozici.', verbose_name='Priorita'),
        ),
    ]