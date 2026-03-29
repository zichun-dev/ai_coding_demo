from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "backsys"
    app_version: str = "0.1.0"
    port: int = 6100
    host: str = "0.0.0.0"
    data_dir: Path = Path(__file__).parent.parent.parent / "data"


settings = Settings()
