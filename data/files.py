import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.sql import func
from data.db_session import SqlAlchemyBase

import datetime


class File(SqlAlchemyBase):
    __tablename__ = 'files'

    id = sqlalchemy.Column(sqlalchemy.String(100), primary_key=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String(200), unique=False, nullable=True)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.String(100), sqlalchemy.ForeignKey("users.id"))
    user = orm.relation("User")

    def __repr__(self):
        return f"<File {self.id} {self.datetime} {self.user_id}>"
