# Generated by Django 4.0.2 on 2022-04-05 22:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_personalchat_personalchatroom_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='personalchat',
            table='personal_chat',
        ),
        migrations.AlterModelTable(
            name='personalchatroom',
            table='personal_chatroom',
        ),
    ]
