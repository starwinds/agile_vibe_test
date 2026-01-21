from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    VALKEY_HOST: str = "localhost"
    VALKEY_PORT: int = 6379
    VALKEY_PASSWORD: str = "valkey"
    VALKEY_INDEX: str = "idx:chunks"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mxbai-embed-large"
    
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "rag_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
