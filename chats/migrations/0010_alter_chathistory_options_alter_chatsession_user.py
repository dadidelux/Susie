# Generated by Django 4.2.6 on 2023-10-21 09:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chats', '0009_chatsession_chathistory_chat_session'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chathistory',
            options={'verbose_name': 'Chat historie'},
        ),
        migrations.AlterField(
            model_name='chatsession',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
