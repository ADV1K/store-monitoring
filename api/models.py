from sqlalchemy import Column, Integer, String, DateTime, Enum

from api.database import Base
from api.enums import StoreStatusEnum, DayOfWeekEnum


class StoreStatus(Base):
    __tablename__ = "store_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, index=True)
    status = Column(Enum(StoreStatusEnum))
    timestamp_utc = Column(DateTime, index=True)


class BusinessHours(Base):
    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, index=True)
    day = Column(Integer, index=True)
    start_time_local = Column(String)
    end_time_local = Column(String)
    timezone_str = Column(String)


class StoreTimezones(Base):
    __tablename__ = "store_timezones"

    store_id = Column(Integer, primary_key=True)
    timezone_str = Column(String, index=True)
