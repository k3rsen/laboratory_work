# -*- coding: utf-8 -*-
import pandas as pd


def describe_column(series):
    """Центр, разброс и положение для одного столбца"""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    return {
        "среднее": round(float(series.mean()), 1),
        "медиана": round(float(series.median()), 1),
        "мода": float(series.mode().iloc[0]),
        "минимум": float(series.min()),
        "максимум": float(series.max()),
        "размах": float(series.max() - series.min()),
        "стандартное отклонение": round(float(series.std()), 1),
        "Q1": float(q1),
        "Q3": float(q3),
        "IQR": float(q3 - q1),
        "коэффициент вариации, %": round(float(series.std() / series.mean() * 100), 1),
    }


def overall_kpi(df):
    """Сводные KPI по всей компании"""
    revenue = df["cost_rub"].sum()
    return {
        "рейсов": int(len(df)),
        "выручка, руб.": int(revenue),
        "средний чек, руб.": round(float(df["cost_rub"].mean())),
        "медианный чек, руб.": round(float(df["cost_rub"].median())),
        "выручка на км, руб.": round(float(revenue / df["distance_km"].sum()), 1),
        "выручка на тонно-км, руб.": round(float(revenue / (df["weight_t"] * df["distance_km"]).sum()), 2),
        "средняя загрузка, т": round(float(df["weight_t"].mean()), 1),
        "OTD, %": round(float((df["delay_h"] == 0).mean() * 100), 1),
        "средняя задержка, ч": round(float(df["delay_h"].mean()), 2),
    }


def kpi_by(df, column):
    """KPI в разрезе любого признака"""
    grouped = df.groupby(column)
    result = grouped.agg(
        trips=("trip_id", "count"),
        revenue=("cost_rub", "sum"),
        avg_ticket=("cost_rub", "mean"),
        avg_weight=("weight_t", "mean"),
        avg_distance=("distance_km", "mean"),
        otd=("delay_h", lambda s: (s == 0).mean() * 100),
    )
    result["rev_per_km"] = grouped["cost_rub"].sum() / grouped["distance_km"].sum()
    return result.round(1).reset_index()


def monthly_dynamics(df):
    """KPI по месяцам с темпами роста к предыдущему месяцу"""
    by_month = kpi_by(df, "month").sort_values("month").reset_index(drop=True)
    by_month["рост рейсов, %"] = (by_month["trips"].pct_change() * 100).round(1)
    by_month["рост выручки, %"] = (by_month["revenue"].pct_change() * 100).round(1)
    return by_month


def frequency(df, column):
    """сколько рейсов и какая доля"""
    counts = df[column].value_counts()
    return pd.DataFrame({column: counts.index, "рейсов": counts.values,
                         "доля, %": (counts.values / len(df) * 100).round(1)})


def cost_distribution(df, bins, labels):
    """Таблица распределения стоимости: доля рейсов х доли выручки"""
    groups = pd.cut(df["cost_rub"], bins=bins, labels=labels)
    table = df.groupby(groups, observed=False)["cost_rub"].agg(["count", "sum"])
    table.columns = ["рейсов", "выручка"]
    table["доля рейсов, %"] = (table["рейсов"] / table["рейсов"].sum() * 100).round(1)
    table["доля выручки, %"] = (table["выручка"] / table["выручка"].sum() * 100).round(1)
    table.index.name = "группа по стоимости"
    return table.reset_index()


def top_trips_share(df, quantile=0.90):
    """Какую долю выручки приносят самые дорогие рейсы"""
    border = df["cost_rub"].quantile(quantile)
    top = df[df["cost_rub"] >= border]
    return {"граница, руб.": round(float(border)),
            "рейсов в топе": int(len(top)),
            "доля выручки, %": round(float(top["cost_rub"].sum() / df["cost_rub"].sum() * 100), 1)}


def _fmt(number):
    """Число с пробелами между"""
    return f"{number:,.0f}".replace(",", " ")


def findings(cost_stats, top, monthly, cv_threshold=30):
    """Автоматические выводы по посчитанным показателям"""
    result = []

    mean, med = cost_stats["среднее"], cost_stats["медиана"]
    gap = (mean / med - 1) * 100
    result.append(f"Средний чек ({_fmt(mean)} руб.) на {gap:.1f}% выше медианного ({_fmt(med)} руб.): "
                  f"крупные рейсы тянут среднее вверх, для денег называйте медиану.")

    cv = cost_stats["коэффициент вариации, %"]
    if cv > cv_threshold:
        result.append(f"Коэффициент вариации стоимости {cv}% (порог {cv_threshold}%): "
                      f"данные сильно разбросаны, одним средним их не описать.")
    else:
        result.append(f"Коэффициент вариации стоимости {cv}%: разброс умеренный.")

    result.append(f"Самые дорогие рейсы (рейсов в топе: {top['рейсов в топе']}, "
                  f"от {_fmt(top['граница, руб.'])} руб.) приносят {top['доля выручки, %']}% выручки.")

    first, last = monthly.iloc[0], monthly.iloc[-1]
    trips_growth = (last["trips"] / first["trips"] - 1) * 100
    rev_growth = (last["revenue"] / first["revenue"] - 1) * 100
    result.append(f"С {first['month']} по {last['month']} число рейсов выросло на {trips_growth:.1f}%, "
                  f"выручка на {rev_growth:.1f}%.")

    if len(monthly) >= 2:
        prev = monthly.iloc[-2]
        ticket_change = (last["avg_ticket"] / prev["avg_ticket"] - 1) * 100
        result.append(f"Средний чек {prev['month']} -> {last['month']}: {ticket_change:+.1f}% "
                      f"(средний вес {prev['avg_weight']} -> {last['avg_weight']} т, "
                      f"средняя дальность {prev['avg_distance']} -> {last['avg_distance']} км).")

    worst = monthly.loc[monthly["otd"].idxmin()]
    result.append(f"OTD: {first['otd']}% в {first['month']} и {last['otd']}% в {last['month']}; "
                  f"минимум {worst['otd']}% в {worst['month']}.")
    return result
