import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://hexlet:12345@localhost:5432/stud_db"
)