# -*- coding: utf-8 -*-
from pathlib import Path

import pandas as pd


def load_trips(raw_dir, filename="trips_q.csv"):
    """Читает журнал рейсов из raw_dir"""
    path = Path(raw_dir) / filename
    if not path.exists():
        raise FileNotFoundError(f"файл {path} не найден (для первого запуска: python make_data.py)")
    df = pd.read_csv(path, parse_dates=["date"])
    print(f"    {path.name}: {len(df)} строк")
    return df
