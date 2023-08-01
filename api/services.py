import pandas as pd

from api.database import engine


def convert_time(row):
    """Convert utc time to local time"""
    return (
        row.timestamp_utc.tz_localize("UTC")  # Add Timezone info
        .tz_convert(row.timezone_str or "America/Chicago")  # Convert to local time
        .tz_localize(None)  # Remove Timezone info
    )


# WIP, but this is the general idea
def calculate_uptime_downtime():
    # Load the CSV into a Pandas DataFrame, and set the timestamp column as utc datetime
    store_status = pd.read_sql_table("store_status", engine, parse_dates=["timestamp_utc"])

    # Add a column for the day of the week
    store_status["day"] = store_status.timestamp_utc.dt.dayofweek

    # Load the business hours
    business_hours = pd.read_sql_table("business_hours", engine, parse_dates=["start_time_local", "end_time_local"])

    # Merge the store status and business hours data, and select the columns we need
    df = pd.merge(store_status, business_hours, on=["store_id", "day"])[
        ["store_id", "status", "day", "timestamp_utc", "start_time_local", "end_time_local", "timezone_str"]
    ]

    # Create a column for timestamp in local time; it's slow because of the convert_time function
    df.timestamp_local = df.apply(convert_time, axis=1)

    # Only keep the rows where the timestamp is between the start and end times
    df = df[
        (df.timestamp_utc.dt.time >= df.start_time_local.dt.time)
        & (df.timestamp_utc.dt.time <= df.end_time_local.dt.time)
    ]

    # Add a new column for the number of minutes the store was open,
    # by subtracting the timestamp_utc by the previous row timestamp_utc
    # and only add if it was active and the day is the same and only if it is between the start and end times
    stores = []
    for store_id, store in df.groupby("store_id"):
        store["minutes_open"] = store.timestamp_utc.diff().dt.total_seconds().div(60).fillna(0).astype(int)
        store["minutes_open"] = store.minutes_open.where(store.status == "active", 0)
        store["minutes_open"] = store.minutes_open.where(store.day == store.day.shift(1), 0)
        store["minutes_open"] = store.minutes_open.where(
            (store.timestamp_utc.dt.time >= store.start_time_local.dt.time)
            & (store.timestamp_utc.dt.time <= store.end_time_local.dt.time),
            0,
        )
        stores.append(store)
