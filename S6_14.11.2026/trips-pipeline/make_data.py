# -*- coding: utf-8 -*-
import csv
import random
from pathlib import Path

random.seed(10)

routes = {
    "Москва-Казань": 820, "Москва-Санкт-Петербург": 710, "Москва-Нижний Новгород": 420,
    "Москва-Воронеж": 520, "Казань-Самара": 360, "Екатеринбург-Челябинск": 220,
    "Новосибирск-Омск": 680, "Санкт-Петербург-Петрозаводск": 430,
}
carriers = ["ТрансЛогистик", "РусКарго", "СибПуть", "ВолгаТранс", "АвтоДорСервис"]
tariffs = {"Контейнер": 7.5, "Нефтепродукты": 9.2, "Зерно": 5.1,
           "Металл": 6.8, "Лес": 4.6, "Стройматериалы": 5.9}
clients = ["Агрохолдинг Нива", "МеталлПром", "СтройБаза 77",
           "НефтеТрейд", "ЛесЭкспорт", "РитейлСеть"]
days_in_month = {2: 28, 3: 31, 4: 30, 5: 31}

rows = []
trip_no = 1
for month in (2, 3, 4, 5):
    n_trips = {2: 190, 3: 215, 4: 240, 5: 265}[month]
    for _ in range(n_trips):
        route, distance = random.choice(list(routes.items()))
        cargo = random.choice(list(tariffs))
        carrier = random.choice(carriers)
        weight = round(min(22.0, max(2.0, random.gauss(13, 4.5))), 1)

        if random.random() < 0.72:
            delay = 0
        else:
            delay = random.choice([1, 1, 2, 2, 3, 4, 6, 8, 12, 18])

        speed = random.uniform(46, 64)
        duration = round(distance / speed + delay, 1)
        cost = distance * weight * tariffs[cargo] * random.uniform(0.94, 1.09)

        rows.append({
            "trip_id": f"T{trip_no:04d}",
            "date": f"2025-{month:02d}-{random.randint(1, days_in_month[month]):02d}",
            "month": f"2025-{month:02d}",
            "route": route,
            "carrier": carrier,
            "cargo_type": cargo,
            "client": random.choice(clients),
            "weight_t": weight,
            "distance_km": distance,
            "duration_h": duration,
            "cost_rub": int(round(cost, -1)),
            "delay_h": delay,
        })
        trip_no += 1

Path("data/raw").mkdir(parents=True, exist_ok=True)
with open("data/raw/trips_q.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Создан data/raw/trips_q.csv: {len(rows)} рейсов")
