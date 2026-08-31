from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_KEYS: str
    ALLOWED_ORIGINS: str = "http://localhost:3000," "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def get_valid_api_keys() -> set[str]:
    return {key.strip() for key in settings.API_KEYS.split(",") if key.strip()}


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
) -> str:
    valid_api_keys = get_valid_api_keys()

    if api_key is None or api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return api_key
