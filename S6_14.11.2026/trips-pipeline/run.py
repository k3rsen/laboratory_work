# -*- coding: utf-8 -*-
"""Точка входа: запускает весь анализ от сырых данных до отчёта."""
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

import config
from src.load import load_trips
from src.prepare import prepare_trips
from src.analyze import (describe_column, overall_kpi, kpi_by, monthly_dynamics,
                         frequency, cost_distribution, top_trips_share, findings)


def df_to_markdown(df):
    """Превращает таблицу в markdown без внешних зависимостей"""
    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "|" + "---|" * len(df.columns)
    rows = ["| " + " | ".join("—" if pd.isna(v) else str(v) for v in row) + " |"
            for row in df.itertuples(index=False)]
    return "\n".join([header, sep] + rows)


def dict_to_lines(d):
    return [f"- **{k}**: {v}" for k, v in d.items()]


def build_report(kpi, quality, cost_stats, top, cost_table, by_carrier, monthly,
                 cargo_freq, notes):
    lines = ["# Отчёт по перевозкам", "",
             "Сформирован: " + datetime.now().strftime("%d.%m.%Y %H:%M")]

    lines += ["", "## Выводы", ""] + [f"- {n}" for n in notes]
    lines += ["", "## Ключевые показатели", ""] + dict_to_lines(kpi)
    lines += ["", "## Стоимость рейса: центр, разброс, положение", ""] + dict_to_lines(cost_stats)
    lines += ["", "## Распределение стоимости: доля рейсов и доля выручки", "",
              df_to_markdown(cost_table)]
    lines += ["", "## Самые дорогие рейсы", ""] + dict_to_lines(top)
    lines += ["", "## По перевозчикам", "", df_to_markdown(by_carrier)]
    lines += ["", "## По месяцам", "", df_to_markdown(monthly)]
    lines += ["", "## Типы груза", "", df_to_markdown(cargo_freq)]
    lines += ["", "## Качество данных", ""] + dict_to_lines(quality)
    return "\n".join(lines)


def main():
    started = datetime.now()
    print("=" * 56)
    print("ЗАПУСК PIPELINE", started.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 56)

    processed = Path(config.PROCESSED_DIR)
    for folder in (processed, Path(config.REPORTS_DIR)):
        folder.mkdir(parents=True, exist_ok=True)

    print("[1/4] загрузка")
    raw = load_trips(config.RAW_DIR, config.TRIPS_FILE)

    print("[2/4] подготовка")
    clean, quality = prepare_trips(raw)
    clean.to_csv(processed / "trips_clean.csv", index=False, encoding="utf-8")
    print(f"    сохранено: {processed / 'trips_clean.csv'} ({len(clean)} строк)")

    print("[3/4] расчёт показателей")
    kpi = overall_kpi(clean)
    cost_stats = describe_column(clean["cost_rub"])
    top = top_trips_share(clean, config.TOP_QUANTILE)
    cost_table = cost_distribution(clean, config.COST_BINS, config.COST_LABELS)
    by_carrier = kpi_by(clean, "carrier").sort_values("revenue", ascending=False)
    by_route = kpi_by(clean, "route").sort_values("revenue", ascending=False)
    monthly = monthly_dynamics(clean)
    cargo_freq = frequency(clean, "cargo_type")
    notes = findings(cost_stats, top, monthly, cv_threshold=config.CV_THRESHOLD)

    by_carrier.to_csv(processed / "kpi_by_carrier.csv", index=False, encoding="utf-8")
    by_route.to_csv(processed / "kpi_by_route.csv", index=False, encoding="utf-8")
    monthly.to_csv(processed / "kpi_by_month.csv", index=False, encoding="utf-8")
    cost_table.to_csv(processed / "cost_distribution.csv", index=False, encoding="utf-8")

    print("[4/4] отчёт")
    report_path = Path(config.REPORTS_DIR) / "report.md"
    report_path.write_text(
        build_report(kpi, quality, cost_stats, top, cost_table, by_carrier, monthly,
                     cargo_freq, notes),
        encoding="utf-8")

    manifest = {
        "запуск": started.isoformat(timespec="seconds"),
        "длительность, с": round((datetime.now() - started).total_seconds(), 2),
        "параметры": {"TRIPS_FILE": config.TRIPS_FILE,
                      "COST_BINS": config.COST_BINS,
                      "TOP_QUANTILE": config.TOP_QUANTILE,
                      "CV_THRESHOLD": config.CV_THRESHOLD},
        "версии": {"python": sys.version, "pandas": pd.__version__},
        "файлы": [{"имя": p.name, "размер, байт": p.stat().st_size}
                  for p in sorted(Path(config.RAW_DIR).glob(config.TRIPS_FILE))],
        "качество данных": quality,
        "итоговые метрики": kpi,
    }
    manifest_path = processed / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                             encoding="utf-8")

    print(f"    {report_path}")
    print(f"    {manifest_path}")
    print("ГОТОВО")
    return manifest


if __name__ == "__main__":
    main()
