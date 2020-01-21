# Generated by Django 3.0 on 2020-01-14 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.CharField(blank=True, max_length=10, null=True, verbose_name='专案')),
                ('build', models.CharField(blank=True, max_length=10, null=True, verbose_name='阶段')),
            ],
            options={
                'verbose_name': '阶段表',
                'verbose_name_plural': '阶段表',
                'db_table': 'Build',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.CharField(blank=True, max_length=10, null=True, verbose_name='专案')),
                ('build', models.CharField(blank=True, max_length=10, null=True, verbose_name='阶段')),
                ('publish_dept', models.CharField(default='', max_length=10, verbose_name='发布部门')),
                ('publisher', models.CharField(blank=True, max_length=20, null=True, verbose_name='发布人')),
                ('publish_status', models.SmallIntegerField(choices=[(0, '已發佈'), (1, '已撤回')], default=0, verbose_name='发布状态')),
                ('publish_time', models.DateTimeField(blank=True, null=True, verbose_name='发布时间')),
                ('subject', models.CharField(blank=True, max_length=64, null=True, verbose_name='主旨')),
                ('order', models.CharField(blank=True, max_length=20, null=True, verbose_name='工单')),
                ('key_content', models.CharField(blank=True, max_length=128, null=True, verbose_name='重点注意流程内容')),
                ('segment', models.CharField(blank=True, max_length=32, null=True, verbose_name='接收段别')),
                ('receiver', models.CharField(blank=True, max_length=20, null=True, verbose_name='接收人')),
                ('receive_status', models.SmallIntegerField(choices=[(0, '未接收'), (1, '已接收')], default=0, verbose_name='接收状态')),
                ('status', models.SmallIntegerField(choices=[(0, 'Ongoing'), (1, 'Closed')], default=0, verbose_name='执行状态')),
                ('withdraw_time', models.DateTimeField(blank=True, null=True, verbose_name='发布时间')),
            ],
            options={
                'verbose_name': '工单基本信息表',
                'verbose_name_plural': '工单基本信息表',
                'db_table': 'OderInfo',
                'ordering': ['-publish_time'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.CharField(blank=True, max_length=10, null=True, verbose_name='专案')),
            ],
            options={
                'verbose_name': '专案表',
                'verbose_name_plural': '专案表',
                'db_table': 'Project',
            },
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('segment', models.CharField(blank=True, max_length=20, null=True, verbose_name='段别')),
            ],
            options={
                'verbose_name': '段别表',
                'verbose_name_plural': '段别表',
                'db_table': 'Segment',
            },
        ),
    ]
