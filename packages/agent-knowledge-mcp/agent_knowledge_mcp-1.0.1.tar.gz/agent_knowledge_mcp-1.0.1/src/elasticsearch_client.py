"""
Elasticsearch client management.
"""
from elasticsearch import Elasticsearch
from typing import Optional, Dict, Any

# Global Elasticsearch client instance
_es_client: Optional[Elasticsearch] = None
_es_config: Optional[Dict[str, Any]] = None


def init_elasticsearch(config: Dict[str, Any]) -> None:
    """Initialize Elasticsearch configuration."""
    global _es_config
    _es_config = config


def get_es_client() -> Elasticsearch:
    """Get or create Elasticsearch client connection."""
    global _es_client, _es_config
    
    if _es_client is None:
        if _es_config is None:
            raise ValueError("Elasticsearch not initialized. Call init_elasticsearch() first.")
        
        es_host = _es_config["elasticsearch"]["host"]
        es_port = _es_config["elasticsearch"]["port"]
        _es_client = Elasticsearch([{'host': es_host, 'port': es_port}])
    
    return _es_client


def reset_es_client() -> None:
    """Reset Elasticsearch client to force reconnection with new config."""
    global _es_client
    _es_client = None
