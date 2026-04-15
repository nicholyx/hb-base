"""Type stubs for hb_base.config."""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application base settings.

    Subclass this in your project to define your own settings.
    """

    app_name: str
    debug: bool

    model_config: dict
