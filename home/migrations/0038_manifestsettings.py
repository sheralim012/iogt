# Generated by Django 3.1.12 on 2021-07-03 16:02

from django.db import migrations, models
import django.db.models.deletion
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('home', '0037_auto_20210701_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManifestSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Provide name', max_length=255, verbose_name='Name')),
                ('short_name', models.CharField(help_text='Provide short name', max_length=255, verbose_name='Short name')),
                ('scope', models.URLField(help_text='Provide scope', verbose_name='Scope')),
                ('background_color', models.CharField(help_text='Provide background color (example: #FFF)', max_length=10, verbose_name='Background color')),
                ('theme_color', models.CharField(help_text='Provide theme color(example: #493174)', max_length=10, verbose_name='Theme color')),
                ('description', models.CharField(help_text='Provide description', max_length=500, verbose_name='Description')),
                ('language', models.CharField(choices=[('ar', 'Arabic'), ('ch', 'Chichewa'), ('en', 'English'), ('fr', 'French'), ('km', 'Khmer'), ('rw', 'Kinyarwanda'), ('rn', 'Kirundi'), ('ku', 'Kurdish'), ('mg', 'Malagasy'), ('ne', 'Nepali'), ('nr', 'Ndebele'), ('pt', 'Portuguese'), ('qu', 'Quechua'), ('ru', 'Russian'), ('sho', 'Shona'), ('es', 'Spanish'), ('sw', 'Swahili'), ('tg', 'Tajik'), ('ti', 'Tigrinya'), ('ur', 'Urdu'), ('uz', 'Uzbek'), ('zu', 'Zulu')], default='en', help_text='Choose language', max_length=3, verbose_name='Language')),
                ('icon_196_196', models.ForeignKey(blank=True, help_text='Add PNG icon 196x196 px (maskable image can be created using https://maskable.app/)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', validators=[home.models.ImageValidator(height=196, width=196)], verbose_name='Icon 196x196 (maskable)')),
                ('icon_512_512', models.ForeignKey(blank=True, help_text='Add PNG icon 512x512 px', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', validators=[home.models.ImageValidator(height=512, width=512)], verbose_name='Icon 512x512')),
                ('icon_96_96', models.ForeignKey(blank=True, help_text='Add PNG icon 96x96 px', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', validators=[home.models.ImageValidator(height=96, width=96)], verbose_name='Icon 96x96')),
            ],
            options={
                'verbose_name': 'Manifest settings',
                'verbose_name_plural': 'Manifests settings',
                'unique_together': {('language', 'scope')},
            },
        ),
    ]
