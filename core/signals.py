from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import CourseDrugSchedule, CourseDose, Course
from .services import regenerate_course_schedule
import datetime

@receiver(post_save, sender=CourseDrugSchedule)
def rebuild_doses(sender, instance: CourseDrugSchedule, **kwargs):
    """
    При сохранении шаблона дозирования очищаем старые и создаём новые CourseDose.
    """
    # Удаляем старые приёмы в рамках курса и шаблона
    CourseDose.objects.filter(
        course=instance.course,
        drug=instance.drug,
        intake_dt__gte=instance.start_time,
        intake_dt__lte=instance.start_time + datetime.timedelta(hours=instance.total_hours)
    ).delete()

    # Генерация новых приёмов
    dt = instance.start_time
    end = instance.start_time + datetime.timedelta(hours=instance.total_hours)
    while dt <= end:
        CourseDose.objects.create(
            course=instance.course,
            drug=instance.drug,
            dose_mg=instance.dose_mg,
            intake_dt=dt
        )
        if instance.interval_h:
            dt += datetime.timedelta(hours=instance.interval_h)
        elif instance.interval_d:
            dt += datetime.timedelta(days=instance.interval_d)
        elif instance.interval_w:
            dt += datetime.timedelta(weeks=instance.interval_w)
        elif instance.weekday is not None:
            # Для приёма 1 раз в неделю
            dt += datetime.timedelta(days=7)
        else:
            break
            
@receiver(post_save, sender=Course)
@receiver(post_delete, sender=Course)
def on_course_change(sender, instance, **kwargs):
    regenerate_course_schedule(instance)

@receiver(post_save, sender=CourseDrugSchedule)
@receiver(post_delete, sender=CourseDrugSchedule)
def on_schedule_change(sender, instance, **kwargs):
    regenerate_course_schedule(instance.course)