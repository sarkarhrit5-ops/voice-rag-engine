"""
Configuration utilities for loading environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def find_env_file():
    """
    Find the .env file in the project root.

    Searches from the voice module directory upward to find .env.
    The voice module is at: voice-rag-engine/voice-rag-engine/voice-rag-engine/voice/
    So .env should be at: voice-rag-engine/voice-rag-engine/voice-rag-engine/.env

    Returns:
        Path: Path to .env file if found, None otherwise
    """
    # Start from this file's directory
    current_dir = Path(__file__).parent  # voice/

    # Go up to project root (voice-rag-engine/voice-rag-engine/voice-rag-engine/)
    project_root = current_dir.parent  # voice-rag-engine/voice-rag-engine/voice-rag-engine/

    env_file = project_root / ".env"
    if env_file.exists():
        return env_file

    # Fallback: check current working directory
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        return cwd_env

    return None


def load_env_config(env_path: str = None) -> bool:
    """
    Load environment variables from .env file.

    Searches for .env in the project root. If env_path is provided,
    loads from that path instead.

    Args:
        env_path: Optional path to .env file. If None, searches for .env
                 in the project root directory.

    Returns:
        bool: True if .env was loaded, False otherwise
    """
    if env_path:
        # Load from explicit path
        if os.path.exists(env_path):
            load_dotenv(env_path, override=False)
            return True
        return False

    # Search for .env in project root
    env_file = find_env_file()
    if env_file:
        load_dotenv(env_file, override=False)
        return True

    return False


def get_config_value(key: str, default: str = None) -> str:
    """
    Get a configuration value from environment.

    Ensures .env is loaded before retrieving the value.

    Args:
        key: Environment variable key
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    # Ensure .env is loaded
    load_env_config()
    return os.getenv(key, default)

