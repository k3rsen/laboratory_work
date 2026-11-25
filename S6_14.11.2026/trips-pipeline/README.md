# Pipeline по перевозкам

Воспроизводимый анализ журнала рейсов (практика 10): описательная статистика,
KPI по перевозчикам, маршрутам и месяцам, автоматический отчёт.

## Запуск

```
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python make_data.py              # один раз: создаёт data/raw/trips_q.csv
python run.py
```

Результат: `reports/report.md`, таблицы в `data/processed/`, манифест запуска
`data/processed/run_manifest.json`.

## Структура

```
config.py        все параметры
make_data.py     генератор исходных данных
run.py           точка входа
src/load.py      слой 1: читает данные
src/prepare.py   слой 2: проверяет и очищает
src/analyze.py   слой 3: считает показатели
data/raw/        исходные данные, только чтение
data/processed/  пересоздаётся при запуске
reports/         пересоздаётся при запуске
```
