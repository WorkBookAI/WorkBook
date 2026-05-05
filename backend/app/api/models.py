from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ModelConfig(BaseModel):
    provider: str  # ollama, lm_studio, openai, anthropic
    model: str
    api_key: str = None
    endpoint: str = None

@router.get("/")
async def list_models():
    """List available models (auto-detect local, list configured APIs)."""
    models = {
        "local": [],
        "api": []
    }

    # TODO: detect Ollama models
    # TODO: detect LM Studio models
    # TODO: list configured API models from config

    return models

@router.post("/test")
async def test_model(config: ModelConfig):
    """Test connection to model."""
    # TODO: test Ollama/LM Studio connection
    # TODO: test API connection
    return {"status": "ok", "model": config.model}

@router.post("/configure")
async def configure_model(config: ModelConfig):
    """Save API key or model configuration."""
    # TODO: encrypt and store API key
    # TODO: validate and save model configuration
    return {"status": "configured", "model": config.model}
