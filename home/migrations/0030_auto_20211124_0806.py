# Generated by Django 3.1.13 on 2021-11-24 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0029_merge_20211111_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='themesettings',
            name='section_card_background_color',
            field=models.CharField(blank=True, default='#ffffff', help_text='The background color of the sub section as a HEX code', max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='themesettings',
            name='section_card_font_color',
            field=models.CharField(blank=True, default='#444', help_text='The background color of the sub section as a HEX code', max_length=8, null=True),
        ),
    ]
