from pydantic_settings import BaseSettings
from pydantic import FilePath, HttpUrl


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///db.sqlite"
    CELERY_BROKER_URL: str = "sqla+sqlite:///db.sqlite"
    CELERY_RESULT_BACKEND: str = "db+sqlite:///db.sqlite"

    BUSINESS_HOURS_DATA_URL: HttpUrl = "http://localhost:8000/sample_data/menu_hours.csv"
    STORE_STATUS_DATA_URL: HttpUrl = (
        "http://localhost:8000/sample_data/store_status.csv"
    )
    STORE_TIMEZONES_DATA_URL: HttpUrl = (
        "http://localhost:8000/sample_data/store_timezones.csv"
    )

    class Config:
        env_file = ".env"


config = Settings()
