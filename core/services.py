from django.db import transaction
import datetime
import math
import warnings
import json
from .models import Course, CourseDrugSchedule, CourseDose

def regenerate_course_schedule(course: "Course"):
    all_doses = []
    for sched in course.drug_schedules.all():
        T_half = sched.drug.decayformula.life_hours
        params = {
            "T_half": T_half,
            "delta_t": sched.delta_t,
            "day_of_week": sched.day_of_week,
            "dose_time": sched.dose_time.strftime("%H:%M"),
            "T_total": course.T_total,
            "D": sched.D,
            "start_time": course.start_time.isoformat(),
        }
        # получаем только doses_dt из функции (нужно её модифицировать, чтобы отдавать и их)
        result, doses_dt = calculate_concentration(**params)

        all_doses += [
            CourseDose(schedule=sched, intake_dt=dt, dose_mg=sched.D)
            for dt in doses_dt
        ]
        # сохраняем concentration_cache если надо
        course.concentration_cache = result

    with transaction.atomic():
        CourseDose.objects.filter(schedule__course=course).delete()
        CourseDose.objects.bulk_create(all_doses)
        course.save()
