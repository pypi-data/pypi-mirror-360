"""Configuration management for refinire-tool-tavily."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """Configuration manager for environment variables and settings."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            env_file: Path to .env file. If None, uses default .env in project root.
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = env_file or self.project_root / ".env"
        self.template_file = self.project_root / ".env.template"
    
    def create_env_from_template(self, overwrite: bool = False) -> bool:
        """Create .env file from template.
        
        Args:
            overwrite: Whether to overwrite existing .env file
            
        Returns:
            True if .env file was created, False if it already exists and overwrite=False
        """
        if self.env_file.exists() and not overwrite:
            print(f".env file already exists at {self.env_file}")
            return False
        
        # Try to generate using oneenv, fallback to existing template or manual creation
        try:
            # Use oneenv to generate template
            result = subprocess.run(
                [sys.executable, "-m", "oneenv", "template"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check if .env.example was created by oneenv
            env_example = self.project_root / ".env.example"
            if env_example.exists():
                import shutil
                shutil.copy2(env_example, self.env_file)
                print("Generated .env file using oneenv template")
            else:
                raise subprocess.CalledProcessError(1, "oneenv template failed")
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback 1: Use existing .env.template
            if self.template_file.exists():
                import shutil
                shutil.copy2(self.template_file, self.env_file)
                print("Created .env file from existing template")
            else:
                # Fallback 2: Create manual template
                manual_template = """# Environment Variables for refinire-tool-tavily
# Copy this file to .env and fill in your actual values

# Tavily API Configuration
# Get your API key from: https://tavily.com/
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Optional: Default search parameters
DEFAULT_MAX_RESULTS=5
DEFAULT_INCLUDE_ANSWER=false
DEFAULT_INCLUDE_RAW_CONTENT=false
"""
                with open(self.env_file, 'w') as f:
                    f.write(manual_template)
                print("Created .env file with manual template")
        
        print(f"Created .env file: {self.env_file}")
        print("Please edit the .env file and set your actual values.")
        return True
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate required configuration using oneenv.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "missing_required": [],
            "warnings": [],
            "errors": []
        }
        
        try:
            # Check TAVILY_API_KEY
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                results["valid"] = False
                results["missing_required"].append("TAVILY_API_KEY")
            elif api_key == "your_tavily_api_key_here":
                results["valid"] = False
                results["warnings"].append("TAVILY_API_KEY is still set to template value")
            
        except Exception as e:
            results["valid"] = False
            results["errors"].append(str(e))
        
        return results
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration values using oneenv.
        
        Returns:
            Dictionary with configuration values
        """
        return {
            "tavily_api_key": os.getenv("TAVILY_API_KEY"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "default_max_results": int(os.getenv("DEFAULT_MAX_RESULTS", "5")),
            "default_include_answer": os.getenv("DEFAULT_INCLUDE_ANSWER", "false").lower() == "true",
            "default_include_raw_content": os.getenv("DEFAULT_INCLUDE_RAW_CONTENT", "false").lower() == "true"
        }
    
    def print_config_status(self) -> None:
        """Print configuration status."""
        print("Configuration Status:")
        print("=" * 20)
        
        validation = self.validate_config()
        
        if validation["valid"]:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has issues:")
            
            if validation["missing_required"]:
                print(f"   Missing required variables: {', '.join(validation['missing_required'])}")
            
            if validation["warnings"]:
                for warning in validation["warnings"]:
                    print(f"   Warning: {warning}")
                    
            if validation["errors"]:
                for error in validation["errors"]:
                    print(f"   Error: {error}")
        
        print()
        print("Current settings:")
        config = self.get_config()
        for key, value in config.items():
            if "api_key" in key.lower() and value:
                # Mask API key for security
                masked_value = value[:8] + "*" * (len(value) - 8) if len(value) > 8 else "*" * len(value)
                print(f"   {key}: {masked_value}")
            else:
                print(f"   {key}: {value}")
    
    def show_env_help(self) -> None:
        """Show environment variable help."""
        print("Environment Variables Help:")
        print("=" * 30)
        print()
        print("🔑 Tavily API Configuration:")
        print("  TAVILY_API_KEY: Tavily API key for web search (REQUIRED)")
        print("                  Get your API key from: https://tavily.com/")
        print()
        print("⚙️  Application Settings:")
        print("  LOG_LEVEL: Logging level (default: INFO)")
        print("            Options: DEBUG, INFO, WARNING, ERROR")
        print()
        print("🔍 Search Defaults:")
        print("  DEFAULT_MAX_RESULTS: Default maximum search results (default: 5)")
        print("  DEFAULT_INCLUDE_ANSWER: Include AI answer by default (default: false)")
        print("  DEFAULT_INCLUDE_RAW_CONTENT: Include raw content by default (default: false)")
        print()
        print("💡 To generate a complete template:")
        print("   oneenv template")


def setup_env() -> None:
    """Setup environment file from template."""
    config_manager = ConfigManager()
    
    if not config_manager.env_file.exists():
        config_manager.create_env_from_template()
    else:
        print(f".env file already exists at {config_manager.env_file}")
    
    config_manager.print_config_status()


def check_config() -> bool:
    """Check if configuration is valid.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    config_manager = ConfigManager()
    validation = config_manager.validate_config()
    
    if not validation["valid"]:
        config_manager.print_config_status()
        print("\nTo fix configuration issues:")
        print("1. Run: python -c 'from refinire_tool_tavily.config import setup_env; setup_env()'")
        print("2. Edit .env file with your actual values")
        return False
    
    return True