# Generated by Django 4.2.20 on 2025-05-02 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_decayformula_life_hours_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseDrugSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dose_mg', models.DecimalField(decimal_places=2, max_digits=7)),
                ('start_time', models.DateTimeField()),
                ('total_hours', models.PositiveIntegerField(help_text='T_total в часах')),
                ('interval_h', models.PositiveSmallIntegerField(blank=True, help_text='delta_t в часах', null=True)),
                ('interval_d', models.PositiveSmallIntegerField(blank=True, help_text='дни (до 99)', null=True)),
                ('interval_w', models.PositiveSmallIntegerField(blank=True, help_text='недели (до 12)', null=True)),
                ('weekday', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')], null=True)),
                ('dose_clock', models.TimeField(help_text='Время приёма (HH:MM)')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drug_schedules', to='core.course')),
                ('drug', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.drug')),
            ],
        ),
    ]
