# src/llm_chat/setup.py
import json
from pathlib import Path
from getpass import getpass


def setup():
    print("Welcome to the LLM Chat setup!")
    print(
        "We'll now collect your API keys. These will be stored securely for future use."
    )

    keys = {}
    providers = ["groq", "openai", "anthropic", "cerebras"]

    for provider in providers:
        key = getpass(f"Enter your {provider.upper()} API key (input will be hidden): ")
        if key:
            keys[f"{provider.upper()}_API_KEY"] = key

    config_dir = Path.home() / ".llm_cli"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump(keys, f)

    print(f"\nAPI keys have been saved to {config_file}")
    print("You can now use the LLM Chat!")


if __name__ == "__main__":
    setup()
