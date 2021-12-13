import datetime

from sqlalchemy import Column, Integer, String, JSON, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String())
    hashed_password = Column(String())
    reset_token = Column(String())
    reset_token_expiration = Column(DateTime)
    created_at = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)


class Signals(Base):
    __tablename__ = 'stock_analysis'

    id = Column(Integer, primary_key=True)
    symbol = Column(String())
    created_at = Column(DateTime)
    pattern = Column(String())
    pattern_type = Column(String())
    sentiment = Column(String())
    total_change = Column(Numeric())
    strength = Column(Integer)
    window_mins = Column(Integer)
    close = Column(Numeric())
    avg_3d_perf = Column(Numeric())


class Stocks(Base):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True)
    symbol = Column(String())
    name = Column(String())
    exchange = Column(String())
