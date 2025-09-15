"""
LangChain integration package for dev-team state machine

Provides LangChain-based LLM integration for development process automation.
Supports Anthropic Claude and OpenAI models with minimal configuration.
"""

from .client import LangChainClient
from .wrapper import chat_with_claude, load_env, install_dependencies

__all__ = [
    'LangChainClient',
    'chat_with_claude', 
    'load_env',
    'install_dependencies'
]