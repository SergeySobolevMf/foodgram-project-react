# Generated by Django 2.2.16 on 2022-08-03 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0006_auto_20220803_2106'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name'], 'verbose_name': 'Ингредиент'},
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='name_ing',
            new_name='name',
        ),
    ]