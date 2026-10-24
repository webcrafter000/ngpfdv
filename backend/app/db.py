import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/postgres"
)

# Normalize bare postgresql:// or postgres:// to use psycopg2 explicitly.
# SQLAlchemy 2.1 defaults a bare scheme to psycopg (v3), which is not 
# installed in this image (only psycopg2-binary is). Render injects 
# DATABASE_URL as a bare postgresql:// string, so this normalization is 
# required for deployment.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
