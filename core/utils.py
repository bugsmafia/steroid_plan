# core/utils.py

import math
import datetime
from typing import List, Tuple, Dict

def compute_concentration(
    dose_events: List[Tuple[datetime.datetime, float]],
    half_life_hours: float,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    step_minutes: int = 60
) -> List[Dict[str, float]]:
    """
    Рассчитывает концентрацию препарата во времени по алгоритму из test_enantat.py.

    Аргументы:
    - dose_events: список кортежей (datetime, dose_mg).
    - half_life_hours: полупериод распада в часах.
    - start_time: время начала расчёта.
    - end_time: время окончания расчёта.
    - step_minutes: шаг времени в минутах.

    Возвращает:
    - список словарей: {'time': datetime, 'conc': концентрация мг/Л}.
    """
    # Коэффициент C0 для дозы: 200 мг -> 0.012 мг/Л
    # значит: C0 = (dose / 200) * 0.012
    timeline: List[Dict[str, float]] = []
    delta = datetime.timedelta(minutes=step_minutes)
    # Порог окончания: 10 полупериодов
    max_decay_duration = 10 * half_life_hours

    t = start_time
    while t <= end_time:
        # время в часах от старта
        t_hours = (t - start_time).total_seconds() / 3600.0
        C_t = 0.0
        # суммируем вклад от каждой дозы
        for dose_time, dose_mg in dose_events:
            if dose_time <= t:
                dt_hours = (t - dose_time).total_seconds() / 3600.0
                if dt_hours <= max_decay_duration:
                    C0 = (dose_mg / 200.0) * 0.012
                    decay_factor = 0.5 ** (dt_hours / half_life_hours)
                    C_t += C0 * decay_factor
        timeline.append({'time': t, 'conc': C_t})
        t += delta

    return timeline
