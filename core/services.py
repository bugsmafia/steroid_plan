# core/services.py

import datetime
import warnings
from django.db import transaction

from .models import Course, CourseDrugSchedule, CourseDose, DecayFormula
from .utils import compute_concentration


def regenerate_course_schedule(course: Course):
    """
    Пересчитывает расписание приёма (CourseDose) и кэш концентрации
    (course.concentration_cache) для заданного курса.
    """
    # 1) Удаляем старые приёмы
    CourseDose.objects.filter(schedule__course=course).delete()

    combined_events = []
    all_doses = []

    # 2) Генерируем события приёма для каждого расписания
    for sched in course.drug_schedules.all():
        # 2.1 получаем полупериод из DecayFormula
        try:
            decay = DecayFormula.objects.get(drug=sched.drug)
            half_life = decay.life_hours
        except DecayFormula.DoesNotExist:
            warnings.warn(
                f"No decay formula for drug id={sched.drug_id}, skipping schedule id={sched.id}"
            )
            continue

        start_dt = course.start_time
        end_dt = start_dt + datetime.timedelta(hours=course.T_total)

        # 2.2 строим список (datetime, dose) — dose_events
        if sched.day_of_week:
            # Приём раз в неделю в определённый день
            day_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2,
                'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
            }
            target = day_map.get(sched.day_of_week.lower())
            if target is None:
                warnings.warn(
                    f"Invalid day_of_week='{sched.day_of_week}' in schedule id={sched.id}, skipping"
                )
                continue

            current = start_dt
            # сдвигаем на первый нужный день недели
            while current.weekday() != target:
                current += datetime.timedelta(days=1)
            current = current.replace(
                hour=sched.dose_time.hour,
                minute=sched.dose_time.minute,
                second=0, microsecond=0
            )

            events = []
            while current <= end_dt:
                events.append((current, sched.D))
                current += datetime.timedelta(weeks=1)

        elif sched.delta_t is not None:
            # Приём с фиксированным интервалом delta_t (в часах)
            interval = datetime.timedelta(hours=sched.delta_t)
            current = start_dt

            events = []
            while current <= end_dt:
                events.append((current, sched.D))
                current += interval
        else:
            # ни delta_t, ни day_of_week не заданы
            warnings.warn(
                f"No delta_t or day_of_week for schedule id={sched.id}, skipping"
            )
            continue

        # 2.3 аккумулируем события и будущие объекты CourseDose
        for dt, dose in events:
            combined_events.append((dt, dose))
            all_doses.append(
                CourseDose(schedule=sched, intake_dt=dt, dose_mg=dose)
            )

    # 3) Сохраняем все найденные CourseDose за одну транзакцию
    with transaction.atomic():
        CourseDose.objects.bulk_create(all_doses)

    # 4) Вычисляем кривую концентрации, если есть события
    if combined_events:
        timeline = compute_concentration(
            combined_events,
            half_life,
            course.start_time,
            end_dt,
            step_minutes=60
        )
        # 5) Форматируем результат для concentration_cache
        V_d = 6.0  # объём распределения (если разный — вынесите в модель)
        cache = [
            [
                point['time'].isoformat(),
                point['time'].day,
                point['time'].hour,
                point['conc'],
                point['conc'] * V_d
            ]
            for point in timeline
        ]
    else:
        cache = []

    # 6) Сохраняем кэш концентрации
    course.concentration_cache = cache
    course.save(update_fields=['concentration_cache'])
