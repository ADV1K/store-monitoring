from datetime import datetime, timedelta
from collections import defaultdict, namedtuple
from typing import Type

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
import pytz

from .database import get_db, Base, engine
from .models import StoreStatus, BusinessHours, StoreTimezones
from .enums import DayOfWeekEnum

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/sample_data", StaticFiles(directory="sample_data"), name="sample_data")


class Timezone(BaseModel):
    store_id: int
    timezone_str: str


class MenuHoursEnum(BaseModel):
    start_time: datetime
    end_time: datetime


DEFAULT_TIMEZONE = "America/Chicago"


@app.get("/")
async def root(db: Session = Depends(get_db)):
    # Get all the store timezones
    store_timezones: dict[int, str] = {}
    for store_tz in db.query(StoreTimezones):
        store_timezones[store_tz.store_id] = store_tz.timezone_str

    # Get menu hours for each store
    menu_hours: dict[int, dict[int, dict]] = defaultdict(dict)
    for store in db.query(BusinessHours):
        menu_hours[store.store_id][store.day] = dict(start_time=store.start_time_utc, end_time=store.end_time_local)

    # Get store status of the last week
    # last_week = datetime.now(timezone.utc) - timedelta(days=7)
    last_week = datetime(2020, 1, 26, tzinfo=pytz.utc) - timedelta(days=7)  # because we only have data for one week
    store_status = (
        db.query(StoreStatus).filter(StoreStatus.timestamp_utc >= last_week).order_by(StoreStatus.timestamp_utc).all()
    )
    for store in store_status:
        store_timezone = store_timezones.get(store.store_id, DEFAULT_TIMEZONE)
        # store.timestamp_utc = store.timestamp_utc.replace(tzinfo=pytz.timezone(store_timezone))

    return 1


@app.get("/trigger_report")
async def trigger_report():
    pass


@app.get("/get_report")
async def get_report():
    pass
