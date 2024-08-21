import logging
import os

import sqlalchemy
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm

logger = logging.getLogger(__name__)

SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init():
    global __factory

    if __factory:
        return

    conn_str = os.getenv("DB_URL")
    logger.info(f"Connecting to db: {conn_str}")

    engine = sqlalchemy.create_engine(
        conn_str, echo=False, pool_size=10, max_overflow=-1
    )
    __factory = sqlalchemy.orm.sessionmaker(bind=engine)

    from . import __all_models  # noqa

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> sqlalchemy.orm.Session:
    global __factory
    return __factory()
