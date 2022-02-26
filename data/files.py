import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.sql import func
from data.db_session import SqlAlchemyBase

from datetime import datetime


class File(SqlAlchemyBase):
    __tablename__ = 'files'

    id = sqlalchemy.Column(sqlalchemy.String(100), primary_key=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR(200), unique=False, nullable=True)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.String(100), sqlalchemy.ForeignKey("users.id"))
    user = orm.relation("User")

    def get_name(self):
        if len(self.name) >= 25:
            return self.name[:25] + "..."
        return self.name

    def get_date(self):
        return self.datetime.strftime("%d %b %H:%M")

    def __repr__(self):
        return f"<File {self.id} {self.datetime} {self.user_id}>"
