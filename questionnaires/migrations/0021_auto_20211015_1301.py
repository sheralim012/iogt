# Generated by Django 3.1.13 on 2021-10-15 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailsvg', '0002_svg_edit_code'),
        ('questionnaires', '0020_auto_20211013_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='icon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailsvg.svg'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='icon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailsvg.svg'),
        ),
        migrations.AddField(
            model_name='survey',
            name='icon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailsvg.svg'),
        ),
    ]
