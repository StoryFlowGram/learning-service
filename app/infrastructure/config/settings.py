from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

class Database(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    user: str = Field(alias="LEARN_DB_USER")
    password: str = Field(alias="LEARN_DB_PASSWORD")
    db_name: str = Field(alias="LEARN_DB_NAME")
    
    host: str = Field(default="learn-db", alias="LEARN_DB_HOST")
    port: int = 5432

    def get_database_url(self, DB_API: str) -> URL:
        return URL.create(
            drivername=f"postgresql+{DB_API}",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.db_name
        )

class Settings:
    def __init__(self):
        self.database = Database()