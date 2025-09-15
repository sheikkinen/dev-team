"""
LangChain Client - Unified LLM interface

IMPORTANT: Changes via Change Management, see CLAUDE.md

Provides a clean, unified interface for LangChain LLM interactions with proper 
error handling and logging. Supports multiple providers (OpenAI, Anthropic) 
with automatic configuration and dependency management.

KEY FILES:
- scripts/langchain_cli.py - Command-line interface
- scripts/llm_langchain.sh - Shell wrapper

KEY FUNCTIONS:
- chat(prompt) - Send prompt to LLM and get response
- analyze_code(code, language) - Specialized code analysis
- get_status() - Check client configuration and availability
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def load_env():
    """Load environment variables from .env file."""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        logger.debug("Loaded environment variables from .env file")


def install_dependencies() -> bool:
    """Check if LangChain dependencies are available."""
    # Temporarily remove paths that could cause module conflicts
    original_path = sys.path.copy()
    project_src = str(Path(__file__).parent.parent)
    paths_to_remove = [p for p in sys.path if project_src in p]
    
    for path in paths_to_remove:
        sys.path.remove(path)
    
    try:
        import langchain_anthropic
        import langchain_core
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Install with: pip install langchain-anthropic langchain-core")
        return False
    finally:
        # Restore original path
        sys.path[:] = original_path


def get_available_models():
    """Get list of available models for each provider."""
    return {
        "anthropic": [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229", 
            "claude-3-opus-20240229"
        ],
        "openai": [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo"
        ]
    }


class LangChainClient:
    """
    Unified client for LangChain LLM interactions.
    
    Provides a simplified interface for common LLM operations with proper
    error handling and logging.
    """
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LangChain client.
        
        Args:
            provider: LLM provider ("openai" or "anthropic"). Defaults to "anthropic".
            model: Specific model to use. Uses provider default if None.
        """
        self.provider = provider or "anthropic"
        self.model = model
        self.api_key = None
        self.llm = None
        
        # Load environment and validate setup
        load_env()
        self._validate_setup()
    
    def _validate_setup(self):
        """Validate that the client can be used."""
        # Check dependencies
        if not install_dependencies():
            raise RuntimeError("LangChain dependencies not available")
        
        # Check API key
        if self.provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        logger.info(f"LangChain client initialized with provider: {self.provider}")
    
    def _get_llm(self):
        """Get or create LLM instance."""
        if self.llm is None:
            # Temporarily remove paths that could cause module conflicts
            original_path = sys.path.copy()
            project_src = str(Path(__file__).parent.parent)
            paths_to_remove = [p for p in sys.path if project_src in p]
            
            for path in paths_to_remove:
                sys.path.remove(path)
            
            try:
                if self.provider == "anthropic":
                    from langchain_anthropic import ChatAnthropic
                    self.llm = ChatAnthropic(
                        api_key=self.api_key,
                        model=self.model or "claude-sonnet-4-20250514",
                        temperature=0.1,
                        max_tokens=4000,
                    )
                elif self.provider == "openai":
                    from langchain_openai import ChatOpenAI
                    self.llm = ChatOpenAI(
                        api_key=self.api_key,
                        model=self.model or "gpt-4o-mini",
                        temperature=0.1,
                        max_tokens=4000,
                    )
            except Exception as e:
                raise RuntimeError(f"Failed to create LLM instance: {e}")
            finally:
                # Restore original path
                sys.path[:] = original_path
        
        return self.llm
    
    def chat(self, prompt: str, **kwargs) -> str:
        """
        Send a chat message and get response.
        
        Args:
            prompt: User prompt/message
            **kwargs: Additional parameters for the LLM
            
        Returns:
            LLM response as string
            
        Raises:
            RuntimeError: If LLM request fails
        """
        # Temporarily remove paths that could cause module conflicts
        original_path = sys.path.copy()
        project_src = str(Path(__file__).parent.parent)
        paths_to_remove = [p for p in sys.path if project_src in p]
        
        for path in paths_to_remove:
            sys.path.remove(path)
        
        try:
            llm = self._get_llm()
            from langchain_core.messages import HumanMessage
            
            messages = [HumanMessage(content=prompt)]
            response = llm.invoke(messages, **kwargs)
            return response.content
                    
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            raise RuntimeError(f"LLM chat failed: {e}")
        finally:
            # Restore original path
            sys.path[:] = original_path
    
    def analyze_code(self, code: str, language: str = "python", task: str = "analyze") -> str:
        """
        Analyze code with a specialized prompt.
        
        Args:
            code: Source code to analyze
            language: Programming language
            task: Analysis task (analyze, review, explain, etc.)
            
        Returns:
            Analysis result
        """
        prompt = f"""
Please {task} the following {language} code:

```{language}
{code}
```

Provide a clear, structured analysis including:
1. Purpose and functionality
2. Code quality observations
3. Potential improvements
4. Architecture patterns used
"""
        
        return self.chat(prompt)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get information about the current client configuration.
        
        Returns:
            Dictionary with client status info
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "has_api_key": bool(self.api_key),
            "api_key_source": "environment" if self.api_key else "not_found",
            "status": "ready" if self.api_key else "not_configured",
            "available_models": get_available_models()
        }


# Legacy compatibility function
def chat_with_claude(prompt: str) -> str:
    """Legacy function for backward compatibility."""
    client = LangChainClient(provider="anthropic")
    return client.chat(prompt)