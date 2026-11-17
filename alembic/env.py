from logging.config import fileConfig

from alembic import context

from database import engine
from models import Base


if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)


if context.is_offline_mode():
    context.configure(
        url=engine.url,
        target_metadata=Base.metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
        )
        with context.begin_transaction():
            context.run_migrations()
