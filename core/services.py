from django.db import transaction
import datetime
import math
import warnings
import json
from .models import Course, CourseDrugSchedule, CourseDose, DecayFormula  
from .utils import compute_concentration

def regenerate_course_schedule(course: "Course"):
    all_doses = []
    CourseDose.objects.filter(schedule__course=course).delete()
    all_results = []
    all_doses  = []
    for sched in course.drug_schedules.all():
        try:
            decay = DecayFormula.objects.get(drug=sched.drug)
            T_half = decay.life_hours
        except DecayFormula.DoesNotExist:
            # можно пропустить или выбросить явную ошибку
            continue
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
        result, doses_dt = compute_concentration(**params)
        
        all_results += result
        all_doses += [
            CourseDose(
                schedule=sched,
                intake_dt=dt,
                dose_mg=sched.D
            )
            for dt in doses_dt
        ]
        # сохраняем concentration_cache если надо
        course.concentration_cache = all_results
        course.save(update_fields=["concentration_cache"])

    with transaction.atomic():
        CourseDose.objects.filter(schedule__course=course).delete()
        CourseDose.objects.bulk_create(all_doses)
        course.save()
