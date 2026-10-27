from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_api_key: str
    llm_model: str
    max_turns: Optional[int] = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


config = Settings()
