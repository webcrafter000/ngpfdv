import os
import json
import datetime
import time
import logging
import requests
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import WindForecast

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Elexon WINDFOR endpoint (Insights API, public, no auth)
WINDFOR_ENDPOINT = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR"

# ---------------------------------------------------------------------------
# Date range configuration – we want the full day for each date param.
# _date_range yields day-start datetimes; the API query parameters
# publishDateTimeFrom and publishDateTimeTo return data for the 24-hour window.
# ---------------------------------------------------------------------------
START_DATE = datetime.datetime(2026, 1, 1)
END_DATE = datetime.datetime(2026, 1, 31, 23, 59, 59)
REQUEST_DELAY_SECONDS = 0.2


def _date_range(start: datetime.datetime, end: datetime.datetime):
    """Yield each day‑start datetime between *start* and *end* inclusive."""
    cur = start
    while cur <= end:
        yield cur
        cur += datetime.timedelta(days=1)


def _fetch_day(date: datetime.datetime) -> list[dict]:
    """Fetch forecast rows for a single day.
    Returns a list of dicts matching the ``wind_forecast`` table schema.
    """
    next_day = date + datetime.timedelta(days=1)
    params = {
        "publishDateTimeFrom": f"{date.strftime('%Y-%m-%d')}T00:00:00Z",
        "publishDateTimeTo": f"{next_day.strftime('%Y-%m-%d')}T00:00:00Z",
    }
    try:
        resp = requests.get(WINDFOR_ENDPOINT, params=params, timeout=30)
        resp.raise_for_status()
    except Exception as exc:
        log.error("Failed to fetch WINDFOR for %s – %s", date.date(), exc)
        return []

    payload = resp.json()
    records: list[dict] = []
    for obj in payload.get("data", []):
        try:
            records.append(
                {
                    "start_time": datetime.datetime.fromisoformat(
                        obj["startTime"].replace("Z", "+00:00")
                    ),
                    "publish_time": datetime.datetime.fromisoformat(
                        obj["publishTime"].replace("Z", "+00:00")
                    ),
                    "generation_mw": float(obj["generation"]),
                }
            )
        except Exception as exc:
            log.debug("Skipping malformed row: %s – %s", obj, exc)
    return records


def _upsert(session: Session, rows: list[dict]) -> None:
    """Bulk upsert into ``wind_forecast`` using the composite PK (start_time, publish_time)."""
    if not rows:
        return
    stmt = insert(WindForecast).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=[WindForecast.start_time, WindForecast.publish_time],
        set_={"generation_mw": stmt.excluded.generation_mw},
    )
    session.execute(stmt)
    session.commit()


def main() -> None:
    total = 0
    min_pub, max_pub = None, None
    with SessionLocal() as db:
        for day in _date_range(START_DATE, END_DATE):
            daily = _fetch_day(day)
            if daily:
                _upsert(db, daily)
                total += len(daily)
                pub_times = [r["publish_time"] for r in daily]
                day_min, day_max = min(pub_times), max(pub_times)
                if min_pub is None or day_min < min_pub:
                    min_pub = day_min
                if max_pub is None or day_max > max_pub:
                    max_pub = day_max
                log.info("[WINDFOR] %s – ingested %d rows", day.date(), len(daily))
            time.sleep(REQUEST_DELAY_SECONDS)
    log.info("[WINDFOR] total rows ingested: %d", total)
    if min_pub and max_pub:
        log.info("[WINDFOR] publish_time range: %s – %s", min_pub.isoformat(), max_pub.isoformat())

if __name__ == "__main__":
    main()
