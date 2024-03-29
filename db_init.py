from data import db_session
import sqlalchemy as sa
from data.__all_models import *

from data.db_types import MYSQL, SQLITE


TYPE = MYSQL
# TYPE = SQLITE


def connect(type):
    def mysql():
        pass
        db_path = "easydrop"
        try:
            with open("data/db_config") as f:
                username, password = f.readline().split()
        except FileNotFoundError:
            raise FileNotFoundError("Create file with name db_config in root with username and password to "
                                    "database separated with space")
        else:
            db_session.global_init(db_path, TYPE, username, password)

    def sqlite():
        db_dir = "db"
        import os
        db_path = os.path.join(db_dir, "easy-drop.sqlite")
        if not os.path.exists(db_dir):
            os.mkdir(db_dir)
        db_session.global_init(db_path, TYPE)

    {
        MYSQL: mysql,
        SQLITE: sqlite
    }.get(type)()


connect(TYPE)
