# Generated by Django 4.2.6 on 2023-10-16 11:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bemas', '0002_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='dms_link',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message='Der <strong><em>d.3</em></strong>-Vorgang muss folgendes Format aufweisen (Beispiele): 512.431-003/002 oder 002.13 oder 114.521-025', regex='^[0-9]{3}\\.[0-9]{1,3}(-[0-9]{3}(\\/[0-9]{3})?)?$')], verbose_name=' d.3'),
        ),
        migrations.AlterField(
            model_name='event',
            name='dms_link',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message='Der <strong><em>d.3</em></strong>-Vorgang muss folgendes Format aufweisen (Beispiele): 512.431-003/002 oder 002.13 oder 114.521-025', regex='^[0-9]{3}\\.[0-9]{1,3}(-[0-9]{3}(\\/[0-9]{3})?)?$')], verbose_name=' d.3'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='dms_link',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message='Der <strong><em>d.3</em></strong>-Vorgang muss folgendes Format aufweisen (Beispiele): 512.431-003/002 oder 002.13 oder 114.521-025', regex='^[0-9]{3}\\.[0-9]{1,3}(-[0-9]{3}(\\/[0-9]{3})?)?$')], verbose_name=' d.3'),
        ),
        migrations.AlterField(
            model_name='originator',
            name='dms_link',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message='Der <strong><em>d.3</em></strong>-Vorgang muss folgendes Format aufweisen (Beispiele): 512.431-003/002 oder 002.13 oder 114.521-025', regex='^[0-9]{3}\\.[0-9]{1,3}(-[0-9]{3}(\\/[0-9]{3})?)?$')], verbose_name=' d.3'),
        ),
    ]