import os
import json
import datetime
import time
import requests
from sqlalchemy.dialects.postgresql import insert

from ..db import SessionLocal
from ..models import WindActual

API_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH"

def fetch_day(date: datetime.date):
    """Fetch WIND actual generation for a single day.
    Queries the Elexon BMRS endpoint for FUELHH records with fuelType=WIND.
    """
    next_date = date + datetime.timedelta(days=1)
    params = {
        "publishDateTimeFrom": f"{date.isoformat()}T00:00:00Z",
        "publishDateTimeTo": f"{next_date.isoformat()}T00:00:00Z",
        "fuelType": "WIND",
    }
    resp = requests.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    for obj in payload.get("data", []):
        if obj.get("fuelType") != "WIND":
            continue
        yield {
            "start_time": datetime.datetime.fromisoformat(
                obj["startTime"].replace("Z", "+00:00")
            ),
            "generation_mw": obj["generation"],
        }

def upsert_rows(rows):
    with SessionLocal() as session:
        for row in rows:
            stmt = insert(WindActual).values(**row).on_conflict_do_update(
                index_elements=["start_time"],
                set_={"generation_mw": row["generation_mw"]},
            )
            session.execute(stmt)
        session.commit()

def main():
    start = datetime.date(2026, 1, 1)
    end = datetime.date(2026, 1, 31)
    total = 0
    min_time = None
    max_time = None
    current = start
    while current <= end:
        rows = list(fetch_day(current))
        if rows:
            upsert_rows(rows)
            total += len(rows)
            times = [r["start_time"] for r in rows]
            min_day = min(times)
            max_day = max(times)
            if min_time is None or min_day < min_time:
                min_time = min_day
            if max_time is None or max_day > max_time:
                max_time = max_day
            print(f"[fuelhh] {current}: ingested {len(rows)} rows")
        # brief pause to be polite to the public endpoint
        time.sleep(0.2)
        current += datetime.timedelta(days=1)
    print(f"[fuelhh] total rows ingested: {total}")
    if min_time and max_time:
        print(f"[fuelhh] start_time range: {min_time.isoformat()} – {max_time.isoformat()}")

if __name__ == "__main__":
    main()
