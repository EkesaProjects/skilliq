import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Candidate Parser"
    DEBUG: bool = True
    UPLOAD_FOLDER: str = Field(default_factory=lambda: os.path.join(os.getcwd(), "uploaded_resumes"))

    # Gemini
    GEMINI_API_KEY: str

    # DB
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()
