"""Common configuration utilities."""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application base settings.

    Subclass this in your project to define your own settings.
    """

    app_name: str = "hb-app"
    debug: bool = False

    model_config = {"env_prefix": "HB_", "env_file": ".env", "extra": "ignore"}
