# Generated by Django 2.0.6 on 2018-07-16 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0012_setup_fixed_charge_configuration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='fk_destination_phone_number',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='destination', to='billing.PhoneNumber'),
        ),
        migrations.AlterField(
            model_name='call',
            name='fk_origin_phone_number',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='origin', to='billing.PhoneNumber'),
        ),
        migrations.AlterField(
            model_name='call',
            name='started_at',
            field=models.DateTimeField(null=True, verbose_name='call started'),
        ),
    ]
