# config.py
import os

class Config:
    # SQLAlchemy URL for SQLite file
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///taskmaster.db")