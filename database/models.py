from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, Boolean, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import relationship

# Создаем базовый класс для декларативных моделей
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True)
    username = Column(Text)
    balance = Column(Float, default=0)
    phone = Column(String(20), unique=True, nullable=True)
    registration_date = Column(DateTime, default=datetime.now(timezone(timedelta(hours=4))))
    utm = Column(Text)

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    event_name = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone(timedelta(hours=4))))

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False)
    add_or_not = Column(Boolean)
    transaction = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.now(timezone(timedelta(hours=4))))
    expires_at = Column(DateTime)
    expire = Column(Boolean, default=False)


class Utm(Base):
    __tablename__ = 'utms'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    statistics = Column(Integer, default=0)

class Remind(Base):
    __tablename__ = 'remindes'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    text_remind = Column(Text)
    date_remind = Column(DateTime)
