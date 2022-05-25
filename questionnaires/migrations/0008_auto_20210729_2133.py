# Generated by Django 3.1.11 on 2021-07-29 21:33

from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0007_auto_20210728_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizformfield',
            name='correct_answer',
            field=models.CharField(help_text='The correct answer/choice(s). For checkboxes: a comma separated list of choices. For checkbox: Either "on" or "off".', max_length=256, verbose_name='correct_answer'),
        ),
        migrations.AlterField(
            model_name='quizformfield',
            name='skip_logic',
            field=wagtail.core.fields.StreamField([('skip_logic', wagtail.core.blocks.StructBlock([('choice', wagtail.core.blocks.CharBlock(required=False)), ('skip_logic', wagtail.core.blocks.ChoiceBlock(choices=[('next', 'Next default question'), ('end', 'End of survey'), ('question', 'Another question')], required=False)), ('question', wagtail.core.blocks.IntegerBlock(required=False))]))], blank=True, help_text='This is used to add choices for field type radio, checkbox, checkboxes, and dropdown only. This can be used to skip questions and skipping is only allowed for radio and dropdown.'),
        ),
        migrations.AlterField(
            model_name='surveyformfield',
            name='skip_logic',
            field=wagtail.core.fields.StreamField([('skip_logic', wagtail.core.blocks.StructBlock([('choice', wagtail.core.blocks.CharBlock(required=False)), ('skip_logic', wagtail.core.blocks.ChoiceBlock(choices=[('next', 'Next default question'), ('end', 'End of survey'), ('question', 'Another question')], required=False)), ('question', wagtail.core.blocks.IntegerBlock(required=False))]))], blank=True, help_text='This is used to add choices for field type radio, checkbox, checkboxes, and dropdown only. This can be used to skip questions and skipping is only allowed for radio and dropdown.'),
        ),
    ]
