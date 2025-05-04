# core/services.py

import datetime
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

    all_doses = []
    combined_events = []

    # 2) Генерируем события приёма для каждого расписания
    for sched in course.drug_schedules.all():
        # Получаем период полураспада из DecayFormula
        try:
            decay = DecayFormula.objects.get(drug=sched.drug)
            half_life = decay.life_hours
        except DecayFormula.DoesNotExist:
            # Если для препарата нет формулы распада — пропускаем
            continue

        start_dt = course.start_time
        end_dt = start_dt + datetime.timedelta(hours=course.T_total)

        if sched.day_of_week:
            # Приём раз в неделю в определённый день
            day_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2,
                'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
            }
            target = day_map[sched.day_of_week.lower()]
            current = start_dt
            # Сдвигаемся на первый нужный день недели
            while current.weekday() != target:
                current += datetime.timedelta(days=1)
            current = current.replace(
                hour=sched.dose_time.hour,
                minute=sched.dose_time.minute,
                second=0, microsecond=0
            )
            # Собираем события каждую неделю
            while current <= end_dt:
                combined_events.append((current, sched.D))
                all_doses.append(
                    CourseDose(schedule=sched, intake_dt=current, dose_mg=sched.D)
                )
                current += datetime.timedelta(weeks=1)
        else:
            # Приём с фиксированным интервалом delta_t (в часах)
            interval = datetime.timedelta(hours=sched.delta_t)
            current = start_dt
            while current <= end_dt:
                combined_events.append((current, sched.D))
                all_doses.append(
                    CourseDose(schedule=sched, intake_dt=current, dose_mg=sched.D)
                )
                current += interval

    # 3) Сохраняем все найденные CourseDose за одну транзакцию
    with transaction.atomic():
        CourseDose.objects.bulk_create(all_doses)

    # 4) Вычисляем кривую концентрации
    #    compute_concentration(doses, half_life_hours, start, end, step_minutes)
    timeline = compute_concentration(
        combined_events,
        half_life,
        course.start_time,
        end_dt,
        step_minutes=60
    )

    # 5) Форматируем результат для сохранения в concentration_cache
    result = []
    V_d = 6.0  # объём распределения, можно вынести в модель, если разный для разных препаратов
    for point in timeline:
        dt = point['time']
        conc = point['conc']
        Q = conc * V_d
        result.append([
            dt.isoformat(),
            dt.day,
            dt.hour,
            conc,
            Q
        ])

    # 6) Сохраняем кэш концентрации
    course.concentration_cache = result
    course.save(update_fields=['concentration_cache'])
