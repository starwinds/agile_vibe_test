from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    VALKEY_HOST: str = "localhost"
    VALKEY_PORT: int = 6379
    VALKEY_PASSWORD: str = "valkey"
    VALKEY_INDEX: str = "idx:chunks"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "nomic-embed-text"

    class Config:
        env_file = ".env"

settings = Settings()
