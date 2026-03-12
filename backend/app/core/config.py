from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # DB
    postgres_db: str = "smart_waste"
    postgres_user: str = "smart_waste"
    postgres_password: str = "smart_waste"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # MQTT
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_telemetry_topic_prefix: str = "bins"

    # External services
    ai_service_url: str = "http://localhost:9000"

    # App
    backend_cors_origins: str = "http://localhost:5173"
    backend_log_level: str = "info"

    # Business thresholds
    full_threshold_pct: float = 85.0

    @property
    def database_url_async(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()

