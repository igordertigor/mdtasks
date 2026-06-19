from pathlib import Path
from typing import Annotated
from pydantic import AfterValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="mdtasks")

    default_context: str = "any"
    project: str = "any"
    root: Annotated[Path, AfterValidator(lambda p: p.expanduser())] = Path("~/.mdtasks")


settings = Settings()
