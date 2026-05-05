from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.llm import LLMManager
from app.core.config import ConfigManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ModelConfig(BaseModel):
    provider: str  # ollama, lm_studio, openai, anthropic
    model: str
    api_key: str = None
    endpoint: str = None

@router.get("/")
async def list_models():
    """List available models."""
    local_models = await LLMManager.detect_local_models()

    return {
        "local": local_models,
        "api": {
            "openai": ["gpt-3.5-turbo", "gpt-4"],
            "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        }
    }

@router.post("/test")
async def test_model(config: ModelConfig):
    """Test connection to model."""
    try:
        provider = LLMManager.get_provider(config.provider, config.model, endpoint=config.endpoint)
        await provider.chat([{"role": "user", "content": "test"}])
        return {"status": "ok", "model": config.model}
    except Exception as e:
        logger.error(f"Model test failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/configure")
async def configure_model(config: ModelConfig):
    """Save API key or model configuration."""
    if config.api_key:
        try:
            ConfigManager.set_api_key(config.provider, config.api_key)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return {"status": "configured", "model": config.model}
