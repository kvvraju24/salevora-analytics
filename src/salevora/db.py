"""One place to open a connection to the project's MySQL database."""
from pathlib import Path

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine

from salevora import config


def has_db_settings() -> bool:
    """True when .env (or the environment) provides a database password."""
    return bool(config.DB_PASSWORD)


def get_engine() -> Engine:
    """Return a SQLAlchemy engine for MySQL, built from the .env settings."""
    url = URL.create(
        "mysql+pymysql",
        username=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
    )
    return create_engine(url)


def run_sql_file(engine: Engine, path: Path) -> None:
    """Run every statement in a .sql file (statements end with ';')."""
    statements = [s.strip() for s in path.read_text().split(";") if s.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.exec_driver_sql(statement)
