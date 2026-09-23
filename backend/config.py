# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://4todo:4todo@localhost:5432/4todo")
