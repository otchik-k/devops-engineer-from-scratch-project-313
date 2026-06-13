from sqlmodel import Field, SQLModel, create_engine

from config import DATABASE_URL

from datetime import datetime


engine = create_engine(DATABASE_URL, echo=False)


class Links(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_url: str
    short_name: str
    short_url: str | None = Field(default=None, nullable=True)
    created_at: datetime | None = Field(default_factory=datetime.now)


def create_tables():
    SQLModel.metadata.create_all(engine)
    print('Создание таблиц в БД')