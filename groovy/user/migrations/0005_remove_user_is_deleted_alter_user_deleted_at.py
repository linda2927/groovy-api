# Generated by Django 4.0.2 on 2022-05-16 17:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user', '0004_remove_user_is_active_user_is_university_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_deleted',
        ),
        migrations.AlterField(
            model_name='user',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
    ]