# core/utils.py

import math
from datetime import datetime, timedelta

def compute_concentration(doses, half_life_hours, 
                          start: datetime, end: datetime,
                          step_minutes: int = 60):
    """
    doses: list of tuples [(dt: datetime, amount_mg: float), …]
    half_life_hours: период полураспада в часах
    start, end: границы расчёта
    step_minutes: шаг сети точек
    → возвращает list of dicts: [{ 'time': datetime, 'conc': float }, …]
    """
    # константа распада
    k = math.log(2) / half_life_hours
    timeline = []
    t = start
    while t <= end:
        total = 0.0
        for dt, amt in doses:
            if dt <= t:
                dt_hours = (t - dt).total_seconds() / 3600.0
                total += amt * math.exp(-k * dt_hours)
        timeline.append({'time': t, 'conc': total})
        t += timedelta(minutes=step_minutes)
    return timeline
