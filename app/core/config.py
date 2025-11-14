
import os

class Settings:
    PROJECT_NAME: str = "Barbearia API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/barbearia_db")

settings = Settings()
