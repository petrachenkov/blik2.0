from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Блик"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./blik.db"
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Active Directory
    AD_SERVER: str = "ldap://ad.example.com"
    AD_BASE_DN: str = "DC=example,DC=com"
    AD_BIND_DN: str = "CN=ServiceAccount,OU=ServiceAccounts,DC=example,DC=com"
    AD_BIND_PASSWORD: str = "service-password"
    AD_USER_SEARCH_FILTER: str = "(sAMAccountName={username})"
    
    # MAX Messenger Bot
    MAX_BOT_TOKEN: str = ""
    MAX_WEBHOOK_URL: str = ""
    
    # Web Interface
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
