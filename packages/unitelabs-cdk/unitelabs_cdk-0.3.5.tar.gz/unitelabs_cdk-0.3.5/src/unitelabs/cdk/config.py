from pydantic_settings import BaseSettings, SettingsConfigDict

import sila


class Config(BaseSettings):
    """Basic Connector configuration."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__", extra="ignore"
    )

    environment: str = "development"
    sila_server: sila.server.ServerConfig = sila.server.ServerConfig()
    cloud_server_endpoint: sila.server.CloudServerConfig = sila.server.CloudServerConfig()
