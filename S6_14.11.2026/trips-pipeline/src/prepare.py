# -*- coding: utf-8 -*-
import pandas as pd

COL = ["trip_id", "date", "month", "route", "carrier", "cargo_type",
            "weight_t", "distance_km", "duration_h", "cost_rub", "delay_h"]
KEY = ["date", "weight_t", "distance_km", "cost_rub", "delay_h"]


def prepare_trips(raw):
    """Очищает журнал рейсов"""
    missing_cols = [c for c in COL if c not in raw.columns]
    if missing_cols:
        raise ValueError(f"в данных нет обязательных столбцов: {missing_cols}")

    report = {"строк получено": len(raw)}
    df = raw.copy()

    df = df.drop_duplicates(subset=["trip_id"], keep="first")
    report["удалено дублей"] = report["строк получено"] - len(df)

    has_gaps = df[KEY].isna().any(axis=1)
    report["удалено: пропуски в ключевых полях"] = int(has_gaps.sum())
    df = df[~has_gaps]

    bad = ((df["weight_t"] <= 0) | (df["distance_km"] <= 0)
           | (df["cost_rub"] <= 0) | (df["delay_h"] < 0))
    report["удалено: неположительные значения"] = int(bad.sum())
    df = df[~bad]

    month_from_date = df["date"].dt.to_period("M").astype(str)
    report["строк, где month не совпал с датой"] = int((month_from_date != df["month"]).sum())

    df["is_delayed"] = df["delay_h"] > 0

    report["строк осталось"] = len(df)
    report["доля потерь, %"] = round((1 - len(df) / report["строк получено"]) * 100, 1)
    return df.reset_index(drop=True), report
