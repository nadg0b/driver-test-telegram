from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str = "sqlite:///./data/database.db"
    bot_token: str = ""
    web_app_url: str = ""

settings = Settings()
