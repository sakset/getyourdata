# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-12 15:31
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data_request', '0026_auto_20160811_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackMessageContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name=b'Created on')),
                ('updated_on', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name=b'Updated on')),
                ('name', models.TextField(default='Default', unique=True)),
                ('header', models.TextField(blank=True, default='Thank you for using [SITE NAME HERE]')),
                ('header_en', models.TextField(blank=True, default='Thank you for using [SITE NAME HERE]', null=True)),
                ('header_fi', models.TextField(blank=True, default='Thank you for using [SITE NAME HERE]', null=True)),
                ('pdf_copy', models.TextField(blank=True, default='A copy of your PDF has been included.', help_text='Included if user requested a copy of his mail request PDF')),
                ('pdf_copy_en', models.TextField(blank=True, default='A copy of your PDF has been included.', help_text='Included if user requested a copy of his mail request PDF', null=True)),
                ('pdf_copy_fi', models.TextField(blank=True, default='A copy of your PDF has been included.', help_text='Included if user requested a copy of his mail request PDF', null=True)),
                ('footer', models.TextField(blank=True, default='Regards,')),
                ('footer_en', models.TextField(blank=True, default='Regards,', null=True)),
                ('footer_fi', models.TextField(blank=True, default='Regards,', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='RequestCopyContent',
        ),
    ]
