from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from ..db import SessionLocal
from ..services.latest_asof import get_latest_forecast

router = APIRouter()

@router.get("/forecast")
def forecast_endpoint(date: str = Query(..., description="Delivery day in YYYY-MM-DD")):
    """Return the latest‑as‑of wind forecast for the supplied delivery day.
    Raises 400 if the date format is invalid.
    """
    try:
        delivery_day = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; expected YYYY-MM-DD")

    with SessionLocal() as session:
        raw_rows = get_latest_forecast(session, delivery_day)
    # Convert timestamps to ISO strings for JSON response
    rows = [
        {
            "start_time": r["start_time"].isoformat(),
            "publish_time": r["publish_time"].isoformat(),
            "generation_mw": r["generation_mw"],
        }
        for r in raw_rows
    ]
    return rows
