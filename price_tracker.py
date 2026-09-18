"""Saves a daily price snapshot and compares it against the most recent
previous one to detect who rose or fell in price."""

import glob
import os
from datetime import date

import pandas as pd


def save_snapshot(df: pd.DataFrame, history_dir: str) -> str:
    os.makedirs(history_dir, exist_ok=True)
    today = date.today().isoformat()
    path = os.path.join(history_dir, f"{today}.csv")
    df[["Player", "Team", "Price"]].to_csv(path, index=False)
    return path


def get_previous_snapshot(history_dir: str) -> pd.DataFrame | None:
    today = date.today().isoformat()
    files = sorted(glob.glob(os.path.join(history_dir, "*.csv")))
    files = [f for f in files if not f.endswith(f"{today}.csv")]
    if not files:
        return None
    return pd.read_csv(files[-1])


def detect_price_changes(current_df: pd.DataFrame, history_dir: str, min_change: float = 0.1) -> pd.DataFrame:
    previous_df = get_previous_snapshot(history_dir)
    if previous_df is None:
        return pd.DataFrame(columns=["Player", "Team", "Old Price", "New Price", "Change"])

    merged = current_df[["Player", "Team", "Price"]].merge(
        previous_df, on=["Player", "Team"], suffixes=("_new", "_old"), how="inner"
    )
    # Round to 2 decimal places - raw float subtraction (e.g. 14.5 - 14.4)
    # can produce values like 0.09999999999999964 instead of 0.1, which
    # would silently fail the threshold check below.
    merged["Change"] = (merged["Price_new"] - merged["Price_old"]).round(2)
    changed = merged[merged["Change"].abs() >= min_change].copy()
    changed = changed.rename(columns={"Price_old": "Old Price", "Price_new": "New Price"})
    changed = changed.sort_values("Change", ascending=False)
    return changed[["Player", "Team", "Old Price", "New Price", "Change"]].reset_index(drop=True)
