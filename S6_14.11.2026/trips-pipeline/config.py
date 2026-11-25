# -*- coding: utf-8 -*-
"""Все параметры анализа в одном месте."""

# пути
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
REPORTS_DIR = "reports"

TRIPS_FILE = "trips_q.csv"

COST_BINS = [0, 20_000, 50_000, 100_000, 1_000_000]
COST_LABELS = ["до 20 тыс", "20-50 тыс", "50-100 тыс", "более 100 тыс"]

TOP_QUANTILE = 0.90      
CV_THRESHOLD = 30        