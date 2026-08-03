from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    ENVIRONMENT: str

    HOST: str
    PORT: int

    FRONTEND_URL: str

    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    REDIS_URL: str

    OPENAI_API_KEY: str = ""
    NEWS_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()