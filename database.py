from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker


engine = create_engine(
    "sqlite:///blogicum.db",
    connect_args={"check_same_thread": False},
)

@event.listens_for(engine, "connect")
def enable_foreign_keys(connection, _):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as session:
        yield session