"""
LangChain integration package for dev-team state machine

Provides LangChain-based LLM integration for development process automation.
Supports Anthropic Claude and OpenAI models with minimal configuration.

Primary interface: LangChainClient for all LLM operations
"""

from .client import LangChainClient, load_env, install_dependencies, get_available_models

__all__ = [
    'LangChainClient',      # Primary interface
    'load_env',            # Utility function
    'install_dependencies', # Utility function
    'get_available_models'  # Utility function
]