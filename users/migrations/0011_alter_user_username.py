# Generated by Django 5.1.3 on 2024-11-18 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_user_telefon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'Bu foydalanuvchi nomi band. Iltimos, boshqa nom kiriting.'}, max_length=150, unique=True),
        ),
    ]