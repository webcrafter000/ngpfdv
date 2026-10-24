"""services/error_calc.py
Utility to calculate forecast error metrics for a delivery day.
"""

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict
from collections import defaultdict

from sqlalchemy.orm import Session

from .latest_asof import get_latest_forecast
from .actuals import get_actuals


def calculate_error_summary(session: Session, delivery_day: date) -> Dict:
    """Compute per‑period errors and summary statistics.

    Returns a dictionary with two top‑level keys:
    * ``rows`` – a list of per‑period dictionaries
      ``{"start_time": ..., "forecast_mw": ..., "actual_mw": ..., "error_mw": ...}``
    * ``aggregates`` – overall MAE, bias, max absolute error, and a list
      ``by_hour`` with hourly MAE and bias.
    """
    # Re-runs the DISTINCT ON query — acceptable at pilot scale (48 rows/day, one month); production would cache per delivery day.
    forecast_rows = get_latest_forecast(session, delivery_day)

    # Retrieve actual generation rows using shared service
    actual_rows = get_actuals(session, delivery_day)

    # WINDFOR is hourly, FUELHH is half-hourly; aggregate actuals to hourly for like-for-like comparison.
    hourly_actuals = defaultdict(list)
    for row in actual_rows:
        hour_key = row["start_time"].replace(minute=0, second=0, microsecond=0)
        hourly_actuals[hour_key].append(row["generation_mw"])

    actual_map = {
        hour: sum(vals) / len(vals)
        for hour, vals in hourly_actuals.items()
    }

    per_period = []
    total_abs_error = 0.0
    total_error = 0.0
    max_abs_error = 0.0

    # Helper to bucket by hour (0‑23) for the hourly summary
    hour_stats: dict[int, dict[str, float]] = {}

    for f in forecast_rows:
        st = f["start_time"]
        forecast = f["generation_mw"]
        actual = actual_map.get(st)
        if actual is None:
            continue
        error = forecast - actual
        abs_err = abs(error)
        per_period.append(
            {
                "start_time": st.isoformat(),
                "forecast_mw": forecast,
                "actual_mw": actual,
                "error_mw": error,
            }
        )
        total_abs_error += abs_err
        total_error += error
        if abs_err > max_abs_error:
            max_abs_error = abs_err

        hour = st.astimezone(ZoneInfo("UTC")).hour
        hour_entry = hour_stats.setdefault(hour, {"abs_sum": 0.0, "err_sum": 0.0, "count": 0})
        hour_entry["abs_sum"] += abs_err
        hour_entry["err_sum"] += error
        hour_entry["count"] += 1

    n = len(per_period)
    mae = total_abs_error / n if n else 0.0
    bias = total_error / n if n else 0.0

    by_hour = []
    for hour in range(24):
        stats = hour_stats.get(hour)
        if stats:
            count = stats["count"]
            hour_mae = stats["abs_sum"] / count if count else 0.0
            hour_bias = stats["err_sum"] / count if count else 0.0
        else:
            hour_mae = 0.0
            hour_bias = 0.0
        by_hour.append({"hour": hour, "mae": hour_mae, "bias": hour_bias})

    return {
        "rows": per_period,
        "aggregates": {
            "mae": mae,
            "bias": bias,
            "max_abs_error": max_abs_error,
            "by_hour": by_hour,
        },
    }
