from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str
    mongodb_database: str
    user_data_encryption_key: str | None = None
    user_lookup_hmac_key: str | None = None
    jwt_secret_key: str | None = None
    jwt_expiration_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
