from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
# from .models import Drug
from django.contrib.postgres.fields import JSONField 
from django.utils import timezone
import calendar
import datetime

from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords



class User(AbstractUser):
    ROLE_CHOICES = [('standard','Standard'),('pro','Pro'),('admin','Admin')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='standard')
    SEX_CHOICES = [('male','Male'),('female','Female'),('other','Other')]
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, blank=True, null=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    EXPERIENCE_CHOICES = [('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced'),('expert','Expert')]
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
User = get_user_model()

class Subscription(models.Model):
    STATUS_CHOICES = [('active','Active'),('expired','Expired'),('cancelled','Cancelled')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    auto_renewal = models.BooleanField(default=False)

# Drug catalogs & relations
class DrugGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Drug(models.Model):
    name = models.CharField(max_length=255)
    group = models.ForeignKey(DrugGroup, on_delete=models.RESTRICT, related_name='drugs')
    sort = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class SideEffect(models.Model):
    name = models.CharField(max_length=255, unique=True)

class DrugSideEffect(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='side_effects')
    effect = models.ForeignKey(SideEffect, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField()
    class Meta:
        unique_together = ('drug','effect')
        constraints = [models.CheckConstraint(check=models.Q(level__gte=0, level__lte=10), name='level_between_0_and_10')]

class IntakeDuration(models.Model):
    drug = models.OneToOneField(Drug, on_delete=models.CASCADE, related_name='intake_duration')
    min_duration_days = models.PositiveIntegerField()
    rec_duration_days = models.PositiveIntegerField()
    max_duration_days = models.PositiveIntegerField()

class DrugCompatibility(models.Model):
    drug_a = models.ForeignKey(Drug, related_name='compatibility_as_a', on_delete=models.CASCADE)
    drug_b = models.ForeignKey(Drug, related_name='compatibility_as_b', on_delete=models.CASCADE)
    compatibility = models.BooleanField(default=False)
    reason = models.TextField(blank=True, null=True)
    class Meta:
        unique_together = ('drug_a','drug_b')
        constraints = [models.CheckConstraint(check=~models.Q(drug_a=models.F('drug_b')), name='no_self_compatibility')]

class EtherType(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='ether_types')
    ether_type = models.CharField(max_length=255)
    class Meta:
        unique_together = ('drug','ether_type')

class ReceptionMethod(models.Model):
    method = models.CharField(max_length=255, unique=True)

class DrugReception(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    reception_method = models.ForeignKey(ReceptionMethod, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('drug','reception_method')

class DrugInfo(models.Model):
    drug = models.OneToOneField(Drug, on_delete=models.CASCADE, related_name='info')
    info = models.TextField(blank=True, null=True)
    half_life_hours = models.DecimalField(max_digits=6, decimal_places=2)
    elimination_hours = models.DecimalField(max_digits=6, decimal_places=2)

class DecayFormula(models.Model):
    drug = models.OneToOneField(Drug, on_delete=models.CASCADE, related_name='decay_formula')
    formula = models.TextField()
    life_hours = models.FloatField()
    def __str__(self):
        return f"{self.drug.name} half-life: {self.life_hours}h"

# Courses and analyses
class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    description = models.TextField(
        blank=True,
        default="",       # даём пустую строку для уже существующих записей
        help_text="Описание курса (опционально)"
    )
    start_time = models.DateTimeField(
        default=timezone.now,
        help_text="Время начала курса (по умолчанию — текущее)"        
    )
    created_at = models.DateTimeField(auto_now_add=True)


    T_total = models.PositiveIntegerField(
        help_text="Длительность приёма в часах",
        default=1680
    )
    # сохраняем в raw JSON параметры, выбранные пользователем:
    schedule_params = models.JSONField(
        default=dict,
        blank=True,
        help_text="Параметры расписания (delta_t, day_of_week и т.д.)"
    )

    # кеш концентрации (тут же можно хранить готовый результат calculate_concentration)
    concentration_cache = models.JSONField(blank=True, null=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.name} ({self.user})"
        
    def recalc_concentration(self):
        from .services import regenerate_course_schedule
        regenerate_course_schedule(self)

class BloodAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blood_analyses')
    analysis_date = models.DateField()
    testosterone = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    prolactin = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    liver_enzymes = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CourseDrugSchedule(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="drug_schedules"
    )
    drug = models.ForeignKey(
        Drug,
        on_delete=models.PROTECT
    )
    D = models.FloatField(
        help_text="Доза в мг",
        null=True,     # временно разрешаем пустое значение
        blank=True,
        default=0.0    # можно использовать default=0.0, чтобы миграция прошла сразу
    )
    # либо fixed interval…
    delta_t = models.FloatField(
        blank=True,
        null=True,
        help_text="Частота в часах"
    )
    # …либо раз в неделю в конкретный день
    day_of_week = models.CharField(
        max_length=9, 
        blank=True, 
        null=True,
        choices=[(d.lower(), d) for d in calendar.day_name],
        help_text='День недели (если приём 1 раз в неделю)'
    )
    dose_time = models.TimeField(
        default=datetime.time(8, 0),
        help_text="Время дозы (по умолчанию 08:00)"
    )
    history = HistoricalRecords()
    def __str__(self):
        return f"{self.drug.name} @ {self.dose_time}"
    
class CourseDose(models.Model):
    schedule = models.ForeignKey(
        CourseDrugSchedule,
        on_delete=models.CASCADE,
        related_name="doses",
        null=True,
        blank=True,
        help_text="Связь на шаблон приёма; временно может быть NULL"
    )
    intake_dt = models.DateTimeField()
    dose_mg    = models.FloatField()  # дублируем на случай коррекции
    history = HistoricalRecords()

    class Meta:
        unique_together = ('schedule', 'intake_dt')

    def __str__(self):
        return f"{self.schedule.drug.name} on {self.intake_dt}"
        
