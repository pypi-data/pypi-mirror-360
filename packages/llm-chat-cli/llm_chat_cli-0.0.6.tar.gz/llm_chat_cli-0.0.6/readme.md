# llm-chat-cli

A CLI tool for chatting with multiple LLM providers in one place.

## Install

```bash
pip install llm-chat-cli
```

## Setup

First time setup:

```bash
lmci setup
```

This will prompt you for your API keys and create a config file.

## Usage

Start chatting:

```bash
lmci
```

## Supported Providers

- Groq
- OpenAI
- Anthropic
- Cerebras

## Commands

- `change model` - Switch models
- `token count` - Show tokens used
- `clear history` - Clear chat history
- `quit`/`exit` - Exit
