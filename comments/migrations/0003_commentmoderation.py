# Generated by Django 3.1.14 on 2022-09-30 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments_xtd', '0008_auto_20200920_2037'),
        ('comments', '0002_cannedresponse_header'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentModeration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('UNMODERATED', 'Unmoderated'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('UNSURE', 'Unsure')], default='UNMODERATED', max_length=255)),
                ('comment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='comment_moderation', to='django_comments_xtd.xtdcomment')),
            ],
        ),
    ]
