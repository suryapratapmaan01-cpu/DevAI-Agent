import os
from dotenv import load_dotenv


load_dotenv()

if "pydantic_settings" in os.sys.modules:
    from pydantic_settings import BaseSettings 
else:
    BaseSettings = object

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")

settings = Settings()
