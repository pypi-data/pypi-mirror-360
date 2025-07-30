import json
from pathlib import Path
import os

# Define the configuration file path in the .llm_cli folder in the user's home directory
CONFIG_FOLDER = Path.home() / ".llm_cli"
CONFIG_FILE = CONFIG_FOLDER / "config.json"


def initialize():
    """
    Initialize the configuration and load API keys.

    Returns:
        dict: Dictionary containing API keys for different providers

    Raises:
        SystemExit: If config file is not found
    """
    if not CONFIG_FILE.exists():
        print("API keys not found. Please run 'lmci setup' first.")
        exit(1)

    with open(CONFIG_FILE, "r") as f:
        api_keys = json.load(f)

    # Load API keys into environment variables
    for provider, key in api_keys.items():
        os.environ[provider] = key

    return api_keys


def load_config():
    """
    Load the configuration, including the default model and provider.

    Returns:
        dict: Dictionary containing the default model and provider
    """
    if not CONFIG_FILE.exists():
        # If no configuration file exists, return a default config
        return {"default_provider": "cerebras", "default_model": "llama-3.3-70b"}

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    return config


def save_config(config):
    """
    Save the configuration, including the default model and provider.

    Args:
        config (dict): The configuration dictionary to be saved
    """
    # Ensure the .llm_cli folder exists
    CONFIG_FOLDER.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
