"""Configuration management for DUKE Agents."""
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration class for DUKE Agents."""
    
    # API Configuration
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = os.getenv("DUKE_MISTRAL_MODEL", "mistral-large-latest")
    CODESTRAL_MODEL: str = os.getenv("DUKE_CODESTRAL_MODEL", "codestral-latest")
    
    # Agent Configuration
    MAX_RETRIES: int = int(os.getenv("DUKE_MAX_RETRIES", "3"))
    SATISFACTION_THRESHOLD: float = float(os.getenv("DUKE_SATISFACTION_THRESHOLD", "0.7"))
    
    # Execution Configuration
    CODE_EXECUTION_TIMEOUT: int = int(os.getenv("DUKE_CODE_EXECUTION_TIMEOUT", "30"))
    ENABLE_SANDBOXED_EXECUTION: bool = os.getenv(
        "DUKE_ENABLE_SANDBOXED_EXECUTION", "true"
    ).lower() == "true"
    
    # Memory Configuration
    MEMORY_RECORD_MAX_SIZE: int = int(os.getenv("DUKE_MEMORY_RECORD_MAX_SIZE", "1000"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("DUKE_LOG_LEVEL", "INFO")
    LOG_FILE: Optional[Path] = Path(os.getenv("DUKE_LOG_FILE")) if os.getenv("DUKE_LOG_FILE") else None
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        if not cls.MISTRAL_API_KEY:
            raise ValueError(
                "MISTRAL_API_KEY is required. "
                "Set it via environment variable or pass it to MistralClient."
            )
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            k: v for k, v in cls.__dict__.items() 
            if not k.startswith('_') and not callable(v)
        }
    
    @classmethod
    def from_env_file(cls, env_file: Path) -> None:
        """Load configuration from .env file."""
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)