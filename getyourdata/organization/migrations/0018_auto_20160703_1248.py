# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-03 12:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0017_auto_20160703_1241'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organizationdraft',
            options={'ordering': ('updated_on',), 'permissions': (('check_organization_draft', 'Can check organization drafts and update the original organization'),), 'verbose_name': 'organization edit draft', 'verbose_name_plural': 'organization edit drafts'},
        ),
    ]
