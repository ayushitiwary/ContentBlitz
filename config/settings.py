from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    serper_api_key: Optional[str] = Field(default=None, env="SERPER_API_KEY")

    # Model Configuration
    model_name: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 2000

    # Vector Store Configuration
    vector_db_path: str = "./data/chromadb"
    collection_name: str = "contentblitz"

    # Content Settings
    blog_min_words: int = 800
    blog_max_words: int = 2000
    linkedin_max_chars: int = 3000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
