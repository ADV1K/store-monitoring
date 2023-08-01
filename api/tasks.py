from functools import partial

import pandas as pd
from celery import Celery
from celery.schedules import crontab

from config import config
from api.database import engine, SessionLocal, Base
from api.models import BusinessHours


app = Celery(__name__, broker=config.CELERY_BROKER_URL, backend=config.CELERY_RESULT_BACKEND)


@app.task
def generate_report():
    pass


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Load the store status data every hour
    sender.add_periodic_task(crontab(minute="5", hour="*"), load_store_status.s(), name="load_store_status")

    # Load the menu hours data every 8 hours
    sender.add_periodic_task(crontab(minute="10", hour="*/8"), load_menu_hours.s(), name="load_menu_hours")

    # Update all the data when the server starts
    load_store_timezones.delay()
    load_store_status.delay()
    load_business_hours.delay()


@app.task
def load_store_status():
    # Load the CSV into a Pandas DataFrame, and set the timestamp column as utc datetime
    df = pd.read_csv(config.STORE_STATUS_DATA_URL.unicode_string(), parse_dates=["timestamp_utc"])

    # Save the DataFrame to the database
    with engine.begin() as con:
        df.to_sql(
            "store_status",
            con=engine,
            if_exists="replace",
            index=True,
            index_label="id",
        )


@app.task
def load_store_timezones():
    df = pd.read_csv(config.STORE_TIMEZONES_DATA_URL.unicode_string())

    # Replace the table with the new data
    with engine.begin() as con:
        df.to_sql(
            "store_timezones",
            con=engine,
            if_exists="replace",
            index=False,
        )


@app.task
def load_business_hours():
    # Load the business hours and store timezones data
    store_timezones = pd.read_csv(config.STORE_TIMEZONES_DATA_URL.unicode_string())
    business_hours = pd.read_csv(
        config.BUSINESS_HOURS_DATA_URL.unicode_string(),
        # parse_dates=["start_time_local", "end_time_local"],
    )

    # Merge the business hours and store timezones data
    df = pd.merge(business_hours, store_timezones, on="store_id")

    # Convert the start and end times to local time then to utc
    # df.start_time_local = df.apply(convert_time_start, axis=1).dt.time
    # df.end_time_local = df.apply(convert_time_end, axis=1).dt.time

    # Change the column names from start_time_local and end_time_local to start_time_utc and end_time_local
    # df.rename(columns={"start_time_local": "start_time_utc", "end_time_local": "end_time_local"}, inplace=True)

    # Change the data types of the start and end times to string
    # df.start_time_utc = df.start_time_utc.astype(str)
    # df.end_time_utc = df.end_time_utc.astype(str)

    # Save the DataFrame to the database
    with SessionLocal() as session:
        # Create the table if it doesn't exist
        Base.metadata.create_all(bind=engine)

        # Delete the old rows
        session.query(BusinessHours).delete()

        # Insert the new rows
        session.bulk_insert_mappings(BusinessHours, df.to_dict(orient="records"))

        # Commit the changes
        session.commit()
