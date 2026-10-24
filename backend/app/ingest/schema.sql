-- Schema for wind data (Elexon)

-- Table for actual wind generation (FUELHH)
CREATE TABLE IF NOT EXISTS wind_actual (
    start_time   TIMESTAMPTZ PRIMARY KEY,
    generation_mw NUMERIC NOT NULL
);

-- Table for wind forecasts (WINDFOR)
CREATE TABLE IF NOT EXISTS wind_forecast (
    start_time    TIMESTAMPTZ NOT NULL,
    publish_time  TIMESTAMPTZ NOT NULL,
    generation_mw NUMERIC NOT NULL,
    PRIMARY KEY (start_time, publish_time)
);

-- Index to efficiently fetch the latest forecast per start_time (publish_time descending)
CREATE INDEX IF NOT EXISTS ix_wind_forecast_start_publish_desc ON wind_forecast (start_time, publish_time DESC);

-- Index on actuals for fast look‑ups by start_time
CREATE INDEX IF NOT EXISTS ix_wind_actual_start ON wind_actual (start_time);

-- Note: publish_time is retained because the "latest‑as‑of" query selects the most recent forecast
-- that was published before the day‑ahead gate‑closure (09:20 GMT on D‑1).
