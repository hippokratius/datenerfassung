# Generated by Django 5.0.6 on 2024-07-04 06:54

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('antragsmanagement', '0006_cleanupeventcontainer_cleanupeven_cleanup_95952b_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CleanupEventDump',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Erstellung')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='letzte Änderung')),
                ('place', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='Müllablageplatz für Müllsammelaktion')),
                ('cleanupevent_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='antragsmanagement.cleanupeventrequest', verbose_name='Antrag')),
            ],
            options={
                'verbose_name': 'Müllsammelaktion: Müllablageplatz',
                'verbose_name_plural': 'Müllsammelaktionen: Müllablageplätze',
                'db_table': 'cleanupevent_dump',
                'ordering': ['-cleanupevent_request'],
                'get_latest_by': 'modified',
                'abstract': False,
                'indexes': [models.Index(fields=['cleanupevent_request'], name='cleanupeven_cleanup_cb488f_idx')],
            },
        ),
    ]