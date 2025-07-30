"""
Client management for different LLM providers
"""

from groq import Groq
from openai import OpenAI
from anthropic import Anthropic
from cerebras.cloud.sdk import Cerebras


def create_clients(api_keys):
    clients = {}
    api_key_mapping = {
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "cerebras": "CEREBRAS_API_KEY",
    }

    for provider, env_var in api_key_mapping.items():
        key = api_keys.get(env_var)
        if key:
            if provider == "groq":
                clients[provider] = Groq(api_key=key)
            elif provider == "openai":
                clients[provider] = OpenAI(api_key=key)
            elif provider == "anthropic":
                clients[provider] = Anthropic(api_key=key)
            elif provider == "cerebras":
                clients[provider] = Cerebras(api_key=key)

    return clients
