import os
import urllib.parse
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MasterPro Copilot API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # AI Provider settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # SQL Server Database settings
    DB_SERVER: str = os.getenv("DB_SERVER", r".\MSSQLSERVER04")
    DB_NAME: str = os.getenv("DB_NAME", "MasterDB")
    DB_USER: str = os.getenv("DB_USER", "haiquan")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "haiquan123")
    DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_TRUST_CERT: str = os.getenv("DB_TRUST_CERT", "yes")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        params = urllib.parse.quote_plus(
            f"DRIVER={{{self.DB_DRIVER}}};"
            f"SERVER={self.DB_SERVER};"
            f"DATABASE={self.DB_NAME};"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD};"
            f"TrustServerCertificate={self.DB_TRUST_CERT};"
        )
        return f"mssql+pyodbc:///?odbc_connect={params}"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()

