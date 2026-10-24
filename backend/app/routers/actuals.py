from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ..db import SessionLocal

router = APIRouter()

@router.get("/actuals")
def actuals_endpoint(date: str = Query(..., description="Delivery day in YYYY-MM-DD")):
    """Return actual wind generation for the supplied delivery day.
    30‑minute rows are returned as ``{start_time, generation_mw}``.
    Raises 400 on malformed date.
    """
    try:
        delivery_day = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; expected YYYY-MM-DD")

    day_start = datetime.combine(delivery_day, datetime.min.time()).replace(tzinfo=ZoneInfo("UTC"))
    day_end = day_start + timedelta(days=1)

    with SessionLocal() as session:
        actual_rows = get_actuals(session, delivery_day)
    # Convert timestamps to ISO strings for JSON response
    rows = [
        {"start_time": r["start_time"].isoformat(), "generation_mw": r["generation_mw"]}
        for r in actual_rows
    ]
    return rows
