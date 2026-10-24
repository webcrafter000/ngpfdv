from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from ..db import SessionLocal
from ..services.error_calc import calculate_error_summary

router = APIRouter()

@router.get("/error-summary")
def error_summary_endpoint(date: str = Query(..., description="Delivery day in YYYY-MM-DD")):
    """Return forecast vs actual error metrics for the supplied delivery day.
    Raises 400 if the date format is invalid.
    """
    try:
        delivery_day = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; expected YYYY-MM-DD")

    with SessionLocal() as session:
        summary = calculate_error_summary(session, delivery_day)
    return summary
