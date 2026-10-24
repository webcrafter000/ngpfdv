import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import forecast, actuals, error

app = FastAPI(title="Wind Forecast Decision Support Portal")

# CORS configuration – allow frontend origin from env, fallback for dev
frontend_origin = os.getenv("FRONTEND_ORIGIN")
# If running in production (ENV=production) we require the variable
if os.getenv("ENV") == "production" and not frontend_origin:
    raise RuntimeError("FRONTEND_ORIGIN environment variable is required in production")
# In non‑production environments fall back to the local Vite dev server
if not frontend_origin:
    frontend_origin = "http://localhost:5173"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(forecast.router, prefix="/api", tags=["forecast"])
app.include_router(actuals.router, prefix="/api", tags=["actuals"])
app.include_router(error.router, prefix="/api", tags=["error"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
