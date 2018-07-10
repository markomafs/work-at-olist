# Generated by Django 2.0.6 on 2018-07-10 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0006_auto_20180703_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='billing',
            name='month',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='billing',
            name='year',
            field=models.IntegerField(default=None),
        ),
        migrations.AlterIndexTogether(
            name='billing',
            index_together={('year', 'month')},
        ),
    ]
