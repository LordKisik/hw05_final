# Generated by Django 2.2.16 on 2022-11-28 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('title',), 'verbose_name': 'категорию', 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'get_latest_by': 'pub_date', 'ordering': ('-pub_date',), 'verbose_name': 'публикацию', 'verbose_name_plural': 'Публикации'},
        ),
    ]