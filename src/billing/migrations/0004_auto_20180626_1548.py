# Generated by Django 2.0.6 on 2018-06-26 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_billingrule'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='billingrule',
            index=models.Index(fields=['is_active'], name='billing_bil_is_acti_df51fa_idx'),
        ),
        migrations.AddIndex(
            model_name='billingrule',
            index=models.Index(fields=['time_start'], name='billing_bil_time_st_2f1714_idx'),
        ),
    ]