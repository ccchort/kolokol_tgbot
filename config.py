import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, field_validator


class Settings(BaseSettings):
    bot_token: SecretStr
    postgres_user: SecretStr
    postgres_password: SecretStr
    postgres_db: SecretStr
    postgres_port: SecretStr
    postgres_host: SecretStr
    admin_ids: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    @field_validator('admin_ids', mode='after')
    @classmethod
    def parse_admin_ids(cls, v: SecretStr) -> list[int]:
        # Извлекаем строку из SecretStr и преобразуем в список чисел
        ids_str = v.get_secret_value()
        if not ids_str:
            return []
        return [int(id.strip()) for id in ids_str.split(',')]




config = Settings()
