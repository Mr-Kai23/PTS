# Generated by Django 3.0 on 2020-04-28 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_process', '0002_auto_20200416_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='key_content',
            field=models.CharField(blank=True, default='', max_length=256, null=True, verbose_name='重点注意流程内容'),
        ),
    ]
