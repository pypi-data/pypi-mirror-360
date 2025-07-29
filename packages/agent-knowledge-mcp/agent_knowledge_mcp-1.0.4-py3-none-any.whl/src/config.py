"""
Configuration management for Elasticsearch MCP Server.
"""
import json
from pathlib import Path
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json file."""
    config_path = Path(__file__).parent / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default configuration if file doesn't exist
        return {
            "elasticsearch": {"host": "localhost", "port": 9200},
            "security": {"allowed_base_directory": "/tmp/knowledge_base_secure"},
            "server": {"name": "elasticsearch-mcp", "version": "0.1.0"}
        }


def get_config() -> Dict[str, Any]:
    """Get the current configuration."""
    return load_config()
