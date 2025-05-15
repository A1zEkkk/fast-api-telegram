import datetime

from src.data.engine import engine

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy import DATE as SQLdate
from typing import List


#Метакласс, который позволяет общаться таблицам
class Base(DeclarativeBase):
    pass


#Таблица зарегистрированных пользователей
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True)
    hash_password: Mapped[str] = mapped_column(String)
    dates: Mapped[List["Date"]] = relationship("Date", back_populates="user")


#Таблица, где хранятся записи пользователей
class Date(Base):
    __tablename__ = "date_and_reminder"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String, ForeignKey('user_account.login'))
    date: Mapped[datetime.date] = mapped_column(SQLdate)
    reminder: Mapped[str] = mapped_column(String)
    user: Mapped[User] = relationship("User", back_populates="dates")

#Создание таблиц, которые унаследованы от Base
Base.metadata.create_all(bind=engine)
