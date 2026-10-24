from sqlalchemy import Column, DateTime, Numeric, PrimaryKeyConstraint, Index
from .db import Base

class WindActual(Base):
    __tablename__ = "wind_actual"
    start_time = Column(DateTime(timezone=True), primary_key=True)
    generation_mw = Column(Numeric, nullable=False)

class WindForecast(Base):
    __tablename__ = "wind_forecast"
    start_time = Column(DateTime(timezone=True), nullable=False)
    publish_time = Column(DateTime(timezone=True), nullable=False)
    generation_mw = Column(Numeric, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint("start_time", "publish_time", name="pk_wind_forecast"),
        Index("ix_wind_forecast_start_publish_desc", "start_time", "publish_time", postgresql_using="btree", postgresql_ops={"publish_time": "DESC"}),
        Index("ix_wind_actual_start", "start_time"),
    )
