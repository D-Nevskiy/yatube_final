# Generated by Django 2.2.16 on 2022-10-06 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='created',
        ),
    ]