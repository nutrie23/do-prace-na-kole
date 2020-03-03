# Generated by Django 2.0.3 on 2018-08-09 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0113_auto_20180806_1155'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campaign',
            options={'ordering': ('-id',), 'permissions': (('can_see_application_links', 'Can see application links'),), 'verbose_name': 'kampaň', 'verbose_name_plural': 'kampaně'},
        ),
        migrations.AddField(
            model_name='campaign',
            name='contact_email',
            field=models.CharField(default='kontakt@dopracenakole.cz', max_length=80, verbose_name='Kontaktní e-mail'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='club_membership_integration',
            field=models.BooleanField(default=True, verbose_name='Povolit integraci s klubem přátel?'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='extra_agreement_text',
            field=models.TextField(blank=True, default='', verbose_name='Další text pro uživatelské souhlas'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='tracks',
            field=models.BooleanField(default=True, verbose_name='Umožnit soutěžícím uložit trasu?'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='recreational',
            field=models.BooleanField(default=False, verbose_name='Započítávají se i rekreační jízdy?'),
        ),
    ]