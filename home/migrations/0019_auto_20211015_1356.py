# Generated by Django 3.1.13 on 2021-10-15 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_auto_20211007_1256'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='allow_comments',
        ),
        migrations.AddField(
            model_name='article',
            name='commenting_ends_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='commenting_starts_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='commenting_status',
            field=models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('disabled', 'Disabled'), ('timestamped', 'Timestamped')], default='open', max_length=15),
            preserve_default=False,
        ),
    ]
