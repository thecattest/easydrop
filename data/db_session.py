import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

from data.db_types import MYSQL, SQLITE

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file, type, username=None, password=None):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise FileNotFoundError("Specify db file")

    if type == SQLITE:
        conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    elif type == MYSQL:
        raise ValueError("MySQL not allowed in this project")
    else:
        raise ValueError("Specify correct database type")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from data import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
