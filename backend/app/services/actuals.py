from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import GATE_CLOSURE_TZ  # not used directly, but keep for consistency


def _day_bounds(delivery_day: date) -> tuple[datetime, datetime]:
    """Return UTC ``day_start`` (inclusive) and ``day_end`` (exclusive)."""
    day_start = datetime.combine(delivery_day, datetime.min.time()).replace(tzinfo=ZoneInfo("UTC"))
    day_end = day_start + timedelta(days=1)
    return day_start, day_end


def get_actuals(session: Session, delivery_day: date) -> List[Dict]:
    """Return actual wind generation rows for *delivery_day*.

    Each dict contains ``{"start_time": datetime, "generation_mw": float}``.
    The caller can serialise ``start_time`` to ISO if needed.
    """
    day_start, day_end = _day_bounds(delivery_day)
    sql = text(
        """
        SELECT start_time, generation_mw
        FROM wind_actual
        WHERE start_time >= :day_start AND start_time < :day_end
        ORDER BY start_time;
        """
    )
    result = session.execute(sql, {"day_start": day_start, "day_end": day_end})
    return [
        {"start_time": row.start_time, "generation_mw": float(row.generation_mw)}
        for row in result.fetchall()
    ]
