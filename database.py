import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username="postgres",
        password=os.environ["POSTGRES_PASSWORD"],
        host="127.0.0.1",
        port=5432,
        database=os.getenv("POSTGRES_DB", "blogicum"),
    )
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as session:
        yield session
