"""services/latest_asof.py

Utility to fetch the *latest‑as‑of* wind forecast for a given delivery day.
The logic follows the product requirement exactly: for each settlement
period (``start_time``) we want the forecast record with the greatest
``publish_time`` that is still on or before the day‑ahead gate‑closure
for that delivery day.

The query is expressed as a single SQL statement using ``DISTINCT ON``
(which is PostgreSQL‑specific).  The full SQL string is shown below for
review.
"""

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import GATE_CLOSURE_HOUR, GATE_CLOSURE_MINUTE, GATE_CLOSURE_TZ
from ..models import WindForecast


def _gate_closure_utc(delivery_day: date) -> datetime:
    """Return the gate‑closure timestamp in UTC.

    Gate‑closure is defined as **09:20 Europe/London** on the day *before*
    the delivery day (D‑1).  We construct a ``datetime`` in the
    ``Europe/London`` timezone and then convert it to UTC for the query.
    """
    # D‑1 (previous calendar day)
    gate_day = delivery_day - timedelta(days=1)
    local_dt = datetime(
        year=gate_day.year,
        month=gate_day.month,
        day=gate_day.day,
        hour=GATE_CLOSURE_HOUR,
        minute=GATE_CLOSURE_MINUTE,
        tzinfo=ZoneInfo(GATE_CLOSURE_TZ),
    )
    # Convert to UTC (the database stores timestamps with tz information)
    return local_dt.astimezone(ZoneInfo("UTC"))


def get_latest_forecast(session: Session, delivery_day: date) -> List[Dict]:
    """Return the latest‑as‑of forecast rows for *delivery_day*.

    The function builds the ``gate_closure`` UTC timestamp, then runs a
    ``DISTINCT ON (start_time)`` query that orders by ``publish_time``
    descending so the first row per ``start_time`` is the most recent
    forecast available before the gate‑closure.
    """
    # Compute the UTC gate‑closure moment for the delivery day
    gate_closure = _gate_closure_utc(delivery_day)

    # Bound the day (inclusive start, exclusive end) – the data are
    # 30‑minute intervals, so a simple midnight‑to‑midnight range works.
    day_start = datetime.combine(delivery_day, datetime.min.time()).replace(tzinfo=ZoneInfo("UTC"))
    day_end = day_start + timedelta(days=1)

    sql = text(
        """
        SELECT DISTINCT ON (wf.start_time)
            wf.start_time,
            wf.publish_time,
            wf.generation_mw
        FROM wind_forecast wf
        WHERE wf.start_time >= :day_start
          AND wf.start_time <  :day_end
          AND wf.publish_time <= :gate_closure
        ORDER BY wf.start_time, wf.publish_time DESC;
        """
    )

    result = session.execute(
        sql,
        {
            "day_start": day_start,
            "day_end": day_end,
            "gate_closure": gate_closure,
        },
    )

    # Convert rows to simple dicts – FastAPI will serialise them to JSON.
    rows = [
        {
            "start_time": r.start_time,
            "publish_time": r.publish_time,
            "generation_mw": float(r.generation_mw),
        }
        for r in result.fetchall()
    ]
    return rows
