Необходимо доработать систему разработки нового курса и его дальнейшая кастомизация.
Пользователь может создать новый курс приема, редактировать его.
Добавлять в созданный курс до 10 препаратов из списка core_drug (по 1 препарату который был выбран в форме из списка).
Выбирает длительность приема (T_total), в кол-ве дней или в кол-ве недель или в количестве месяцев.
Выбирает вариант частоты приема, с выбором указания кол-ва часов (до 24 часов) или  количества дней или кол-во недель (до 99) или кол-во месяев (до 12). Либо указывает day_of_week определенный день недели (получается частота приема раз в неделю в определенный день).
Указывает дозировку препарата в mg (D).

# Пример запуска
T_half = 108       # Полуразпад препарата core_decayformula.life_hours
delta_t = 72     # Не используется, если указан day_of_week. Частота приема препарата
day_of_week = "Wednesday"  # Прием каждую среду. Иной формат если выбран определенный день недели.
dose_time = "10:00"  # Время приема
T_total = 1680     # 10 недель. Длительность приема в часах. С формы данные по кол-ву дней или недели или месяца необходимо переводить в часы
D = 200            # Доза 200 мг. Данные из формы дозировка используемого препарата
start_time = "2025-05-02T15:00:00"  # Начало расчета. С форме должен быть календарь, по умолчанию в инпут текущий день и прием в начале следующего часа.

Все это сохранять в базу данных.
Скрипт расчета def calculate_concentration на основе данных с формы формирует график приема препарата (и добавляет это в календарь, в ячейке дня могут быть разные препараты). Это необходимо сохранить в бд, что бы не проводить перерасчет каждый раз. 

Необходимо сделать система напоминания приема препарата в виде алерта или блока информации:
    Сегодня: Не обходимо принять препарат Тестостерон в дозировке 200mg.
    Завтра: Прием препаратов не нужен.
    
В календаре плана приема должна быть возможность изменить время или день приема препарата (если человек забыл его принять и принял в другое время). При изменении даннных в календаре на основе логики построения концентрации препарата в организме и его скорость распада (как было сделано в calculate_concentration) должен произойти перерасчет концентрации препарата в организме.

Данные о скорости распада core_decayformula
drug_id, life_hours (число с точкой)

Должен сформировать удобный формат плана приема в виде календаря.
Под календарем чарт график с концентрацией препарата за каждый час (возможность zoom по датам)



import math
import warnings
import json
import datetime
import matplotlib.pyplot as plt
import calendar

def calculate_concentration(
    T_half, 
    delta_t=None, 
    day_of_week=None, 
    dose_time="08:00", 
    T_total=1680, 
    D=200, 
    V_d=6.0, 
    threshold=0.0001, 
    start_time=None
):
    """
    Рассчитывает концентрацию тестостерона в крови (мг/Л) и количество препарата в организме (мг),
    формируя график-календарь с отметками приемов.

    Параметры:
    - T_half (float): Полуразпадный период в часах (например, 108 для энантата).
    - delta_t (float): Интервал между дозами в часах (например, 168 для еженедельного приема).
    - day_of_week (str): День недели для приема (например, 'Wednesday'). Игнорируется, если указан delta_t.
    - dose_time (str): Время приема в формате 'HH:MM' (по умолчанию '08:00').
    - T_total (float): Длительность лечения в часах (например, 1680 для 10 недель).
    - D (float): Доза в мг (от 1 до 5000 мг).
    - V_d (float): Объем распределения в литрах (по умолчанию 6.0 Л).
    - threshold (float): Порог концентрации в мг/Л для полного распада (по умолчанию 0.0001).
    - start_time (str): Дата/время начала в формате ISO (например, '2025-05-02T14:00:00').
                       Если None, используется текущая дата/время.

    Возвращает:
    - Список списков: [Дата (ISO), День, Час, Концентрация (мг/Л), Количество препарата (мг)].
    - Создает JSON-файл и график-календарь.

    Предупреждения:
    - Для доз < 50 мг или > 400 мг расчет концентрации может быть неточным.
    """
    # Проверка дозы
    if D < 50 or D > 400:
        warnings.warn(
            f"Доза {D} мг выходит за пределы стандартного диапазона (50–400 мг). "
            "Расчет концентрации может быть неточным."
        )

    # Начальная концентрация: 200 мг дает ~0.012 мг/Л (1200 нг/дЛ)
    C0 = (D / 200) * 0.012

    # Установка времени начала
    if start_time is None:
        start_dt = datetime.datetime.now()
    else:
        start_dt = datetime.datetime.fromisoformat(start_time)

    # Парсинг времени приема для day_of_week
    dose_hour, dose_minute = map(int, dose_time.split(":"))

    # Генерация моментов времени для доз
    doses = []
    doses_dt = []  # Для календаря (даты в формате datetime)
    t_dose = 0

    if day_of_week:
        # Прием в определенный день недели
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_day = day_map.get(day_of_week.lower())
        if target_day is None:
            raise ValueError("Недопустимый день недели. Используйте: Monday, Tuesday, и т.д.")

        # Найти первый подходящий день недели
        current_dt = start_dt
        while current_dt.weekday() != target_day:
            current_dt += datetime.timedelta(days=1)
        current_dt = current_dt.replace(hour=dose_hour, minute=dose_minute, second=0, microsecond=0)

        # Генерация доз каждую неделю
        while t_dose <= T_total:
            doses.append(t_dose)
            doses_dt.append(current_dt)
            current_dt += datetime.timedelta(weeks=1)
            t_dose = (current_dt - start_dt).total_seconds() / 3600
    else:
        # Прием с фиксированным интервалом
        if delta_t is None:
            raise ValueError("Необходимо указать delta_t или day_of_week")
        current_dt = start_dt
        while t_dose <= T_total:
            doses.append(t_dose)
            doses_dt.append(current_dt)
            t_dose += delta_t
            current_dt += datetime.timedelta(hours=delta_t)

    # Продолжение расчета до полного распада
    last_dose = max(doses)
    T_extended = last_dose + 10 * T_half

    # Расчет концентрации и количества препарата
    result = []
    t_m = 0
    while t_m <= T_extended:
        current_dt = start_dt + datetime.timedelta(hours=t_m)
        day = math.floor(t_m / 24)
        hour = t_m % 24

        C_t = 0.0
        for t_d in doses:
            if t_d <= t_m and (t_m - t_d) <= 10 * T_half:
                decay = (t_m - t_d) / T_half
                C_t += C0 * (0.5 ** decay)

        if t_m > last_dose and C_t < threshold:
            break

        Q_t = C_t * V_d
        result.append([current_dt.isoformat(), day, hour, C_t, Q_t])
        t_m += 3

    # Создание календаря
    year = start_dt.year
    month = start_dt.month
    cal = calendar.monthcalendar(year, month)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f"Календарь приемов (доза {D} мг, {year}-{month:02d})")
    ax.set_xlabel("День недели")
    ax.set_ylabel("Неделя")

    # Настройка осей
    ax.set_xticks(range(7))
    ax.set_xticklabels(['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'])
    ax.set_yticks(range(len(cal)))
    ax.set_yticklabels([f"Неделя {i+1}" for i in range(len(cal))])

    # Отметки приемов
    for dose_dt in doses_dt:
        if dose_dt.year == year and dose_dt.month == month:
            day = dose_dt.day
            hour = dose_dt.hour
            for week_idx, week in enumerate(cal):
                if day in week:
                    day_idx = week.index(day)
                    ax.plot(day_idx, week_idx, 'ro', markersize=10, label='Прием' if week_idx == 0 and day_idx == 0 else '')
                    ax.text(day_idx, week_idx + 0.2, f"{hour:02d}:00", ha='center', fontsize=8)

    ax.legend()
    plt.grid(True)
    plt.savefig("calendar_doses.png")
    plt.show()

    return result

# Пример запуска
T_half = 108       # Полуразпад для энантата
delta_t = 72     # Не используется, если указан day_of_week
day_of_week = "Wednesday"  # Прием каждую среду
day_of_week = None  # Прием каждую среду
dose_time = "10:00"  # Время приема
T_total = 1680     # 10 недель
D = 200            # Доза 200 мг
start_time = "2025-05-02T15:00:00"  # Начало расчета

# Выполнение расчета
results = calculate_concentration(
    T_half, delta_t, day_of_week, dose_time, T_total, D, start_time=start_time
)

# Табличный вывод
print("Первые 5 результатов:")
print("Дата и время                | День | Час | Концентрация (мг/Л) | Количество (мг)")
print("-" * 70)
for i in range(5):
    dt, day, hour, C_t, Q_t = results[i]
    print(f"{dt:26} | {day:4} | {hour:3} | {C_t:18.6f} | {Q_t:14.6f}")

print("\nПоследние 5 результатов:")
print("Дата и время                | День | Час | Концентрация (мг/Л) | Количество (мг)")
print("-" * 70)
for i in range(-5, 0):
    dt, day, hour, C_t, Q_t = results[i]
    print(f"{dt:26} | {day:4} | {hour:3} | {C_t:18.6f} | {Q_t:14.6f}")

# JSON-вывод
json_results = [
    {
        "datetime": dt,
        "day": day,
        "hour": hour,
        "concentration_mg_per_L": C_t,
        "amount_mg": Q_t
    }
    for dt, day, hour, C_t, Q_t in results
]

print("\nJSON-вывод (первые 5 записей):")
print(json.dumps(json_results[:5], indent=2, ensure_ascii=False))

# Сохранение JSON
with open("testosterone_concentration.json", "w", encoding="utf-8") as f:
    json.dump(json_results, f, indent=2, ensure_ascii=False)
print("\nПолный JSON сохранен в файл 'testosterone_concentration.json'")