from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str = "https://your-project-ref.supabase.co"
    SUPABASE_KEY: str = "dev_placeholder_key"
    JWT_SECRET: str = "dev_secret_change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FRONTEND_ORIGINS: str = "http://localhost:5173,http://localhost:8501"

    class Config:
        env_file = ".env"


settings = Settings()
