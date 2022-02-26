import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin

from hashlib import md5
from werkzeug.security import check_password_hash, generate_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String(100), primary_key=True, unique=True)
    login = sqlalchemy.Column(sqlalchemy.VARCHAR(255), unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String(110), nullable=True)

    files = orm.relation("File", back_populates="user")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User {self.id} {self.login}>"
