"""
LangChainClient - High-level client for LLM interactions

IMPORTANT: Changes via Change Management, see CLAUDE.md

Provides a clean interface for LangChain LLM interactions with proper error handling and logging.
Supports multiple providers (OpenAI, Anthropic) with automatic configuration and dependency management.
Designed to integrate seamlessly with the dev-team state machine workflow system.

KEY FILES:
- src/langchain_integration/wrapper.py - Core LangChain functionality
- scripts/llm_langchain.sh - Shell wrapper for command-line usage
- config/langchain_hello_world.yaml - State machine integration example

KEY FUNCTIONS:
- chat(prompt) - Send prompt to LLM and get response
- analyze_code(code, language) - Specialized code analysis
- get_status() - Check client configuration and availability
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import os
import sys

logger = logging.getLogger(__name__)


class LangChainClient:
    """
    High-level client for LangChain LLM interactions.
    
    Provides a simplified interface for common LLM operations with proper
    error handling and logging, following dev-team project patterns.
    """
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LangChain client.
        
        Args:
            provider: LLM provider ("openai" or "anthropic"). Auto-detected if None.
            model: Specific model to use. Uses default if None.
        """
        self.provider = provider or "anthropic"  # Default to Anthropic
        self.model = model
        self.api_key = None
        self.llm = None
        
        # Load environment and initialize
        self._load_environment()
        self._validate_setup()
    
    def _load_environment(self):
        """Load environment variables from .env file."""
        try:
            from .wrapper import load_env
            load_env()
            logger.debug("Environment variables loaded")
        except Exception as e:
            logger.warning(f"Failed to load environment: {e}")
    
    def _validate_setup(self):
        """Validate that the client can be used."""
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
            # Install dependencies if needed
            from .wrapper import install_dependencies
            if not install_dependencies():
                raise RuntimeError("Failed to install LangChain dependencies")
            
            # Create LLM instance with path management to avoid conflicts
            original_path = sys.path.copy()
            project_src = str(Path(__file__).parent.parent)
            if project_src in sys.path:
                sys.path.remove(project_src)
            
            try:
                if self.provider == "anthropic":
                    from langchain_anthropic import ChatAnthropic
                    self.llm = ChatAnthropic(
                        api_key=self.api_key,
                        model=self.model or "claude-3-haiku-20240307",
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
        try:
            from .wrapper import chat_with_claude
            if self.provider == "anthropic":
                return chat_with_claude(prompt)
            else:
                # For other providers, use direct LLM access
                llm = self._get_llm()
                from langchain_core.messages import HumanMessage
                
                # Remove project path to avoid conflicts
                original_path = sys.path.copy()
                project_src = str(Path(__file__).parent.parent)
                if project_src in sys.path:
                    sys.path.remove(project_src)
                
                try:
                    messages = [HumanMessage(content=prompt)]
                    response = llm.invoke(messages, **kwargs)
                    return response.content
                finally:
                    sys.path[:] = original_path
                    
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            raise RuntimeError(f"LLM chat failed: {e}")
    
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
            "status": "ready" if self.api_key else "not_configured"
        }