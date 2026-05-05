from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional
import json

class Settings(BaseSettings):
    workbook_dir: Path = Path.home() / ".workbook"
    db_path: Path = workbook_dir / "workbook.db"
    config_file: Path = workbook_dir / "config.json"
    gemini_api_key: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()

class ConfigManager:
    @staticmethod
    def load_config() -> dict:
        """Load config from file."""
        settings.config_file.parent.mkdir(parents=True, exist_ok=True)
        if settings.config_file.exists():
            with open(settings.config_file, 'r') as f:
                return json.load(f)
        return {"api_keys": {}, "local_models": {}}

    @staticmethod
    def save_config(config: dict) -> None:
        """Save config to file."""
        with open(settings.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    @staticmethod
    def get_api_key(provider: str) -> Optional[str]:
        """Get API key for provider."""
        config = ConfigManager.load_config()
        return config.get("api_keys", {}).get(provider)

    @staticmethod
    def set_api_key(provider: str, key: str) -> None:
        """Set API key for provider."""
        config = ConfigManager.load_config()
        if "api_keys" not in config:
            config["api_keys"] = {}
        config["api_keys"][provider] = key
        ConfigManager.save_config(config)
