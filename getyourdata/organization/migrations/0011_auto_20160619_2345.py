# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-19 23:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0010_auto_20160610_1308'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ('created_on',)},
        ),
    ]