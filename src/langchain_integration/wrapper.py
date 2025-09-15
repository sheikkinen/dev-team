"""
LangChain wrapper core functionality

IMPORTANT: Changes via Change Management, see CLAUDE.md

Core LangChain integration functions for the dev-team project. Provides low-level 
LangChain functionality with careful path management to avoid module conflicts.
Handles environment loading, dependency installation, and direct LLM communication.

KEY FUNCTIONS:
- load_env() - Load environment variables from .env file
- install_dependencies() - Install required LangChain packages
- chat_with_claude(prompt) - Direct Claude interaction via LangChain
"""

import os
import sys
import logging
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
    else:
        logger.debug("No .env file found")


def install_dependencies() -> bool:
    """Check if LangChain dependencies are available."""
    # Remove any paths that could cause conflicts with built-in modules
    import sys
    from pathlib import Path
    
    original_path = sys.path.copy()
    # Remove paths that contain our src directory to avoid conflicts
    paths_to_remove = []
    for path in sys.path:
        path_obj = Path(path)
        if path_obj.name == 'src' or 'src/queue' in str(path_obj):
            paths_to_remove.append(path)
    
    for path in paths_to_remove:
        if path in sys.path:
            sys.path.remove(path)
    
    try:
        import langchain_anthropic
        import langchain_core
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Install with: pip install langchain-anthropic langchain-core python-dotenv")
        return False
    finally:
        # Restore original path
        sys.path[:] = original_path


def chat_with_claude(prompt: str) -> str:
    """
    Send prompt to Claude via LangChain and return response.
    
    Args:
        prompt: User prompt to send to Claude
        
    Returns:
        Claude's response as string
        
    Raises:
        ValueError: If API key not found
        RuntimeError: If LangChain request fails
    """
    # Remove any paths that could cause conflicts with built-in modules
    import sys
    from pathlib import Path
    
    original_path = sys.path.copy()
    # Remove paths that contain our src directory to avoid conflicts
    paths_to_remove = []
    for path in sys.path:
        path_obj = Path(path)
        if path_obj.name == 'src' or 'src/queue' in str(path_obj):
            paths_to_remove.append(path)
    
    for path in paths_to_remove:
        if path in sys.path:
            sys.path.remove(path)
    
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage
        
        # Get API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        # Create LLM instance
        llm = ChatAnthropic(
            api_key=api_key,
            model="claude-3-haiku-20240307",
            temperature=0.1,
            max_tokens=4000,
        )
        
        # Send message and get response
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        
        logger.debug(f"Claude response received: {len(response.content)} characters")
        return response.content
    
    except Exception as e:
        logger.error(f"Claude chat failed: {e}")
        raise RuntimeError(f"LangChain Claude communication failed: {e}")
    
    finally:
        # Restore original path
        sys.path[:] = original_path


def get_available_models():
    """Get list of available models for each provider."""
    return {
        "anthropic": [
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


def check_setup():
    """
    Check LangChain setup status.
    
    Returns:
        Dictionary with setup information
    """
    setup_info = {
        "anthropic_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "available_models": get_available_models(),
        "dependencies_installed": False
    }
    
    # Check if dependencies are available
    original_path = sys.path.copy()
    # Remove paths that contain our src directory to avoid conflicts
    paths_to_remove = []
    for path in sys.path:
        path_obj = Path(path)
        if path_obj.name == 'src' or 'src/queue' in str(path_obj):
            paths_to_remove.append(path)
    
    for path in paths_to_remove:
        if path in sys.path:
            sys.path.remove(path)
    
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage
        setup_info["dependencies_installed"] = True
    except ImportError:
        setup_info["dependencies_installed"] = False
    finally:
        sys.path[:] = original_path
    
    setup_info["ready"] = (
        setup_info["dependencies_installed"] and 
        (setup_info["anthropic_key"] or setup_info["openai_key"])
    )
    
    return setup_info