# Generated by Django 5.0.7 on 2024-07-28 22:25

import datetime
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ranking', '0003_alter_match_comment_alter_player_auth_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='match',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
