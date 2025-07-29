"""
Admin tool handlers.
"""
import json
from pathlib import Path
from typing import List, Dict, Any

import mcp.types as types
from .config import load_config
from .security import get_allowed_base_dir, set_allowed_base_dir, init_security
from .elasticsearch_client import reset_es_client, init_elasticsearch
from .elasticsearch_setup import auto_setup_elasticsearch, ElasticsearchSetup


async def handle_get_allowed_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_allowed_directory tool."""
    return [
        types.TextContent(
            type="text",
            text=f"Current allowed base directory: {get_allowed_base_dir()}"
        )
    ]


async def handle_set_allowed_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle set_allowed_directory tool."""
    directory_path = arguments.get("directory_path")
    
    try:
        new_path = Path(directory_path).resolve()
        
        if not new_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not new_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory_path}")
        
        old_path = set_allowed_base_dir(new_path)
        
        return [
            types.TextContent(
                type="text",
                text=f"Allowed base directory changed from '{old_path}' to '{get_allowed_base_dir()}'"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error setting allowed directory to '{directory_path}': {str(e)}"
            )
        ]


async def handle_reload_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle reload_config tool."""
    try:
        # Reload configuration
        config = load_config()
        
        # Reinitialize security with new allowed directory
        init_security(config["security"]["allowed_base_directory"])
        
        # Reinitialize Elasticsearch with new config
        init_elasticsearch(config)
        reset_es_client()
        
        return [
            types.TextContent(
                type="text",
                text=f"Configuration reloaded successfully.\nNew allowed directory: {get_allowed_base_dir()}\nElasticsearch: {config['elasticsearch']['host']}:{config['elasticsearch']['port']}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error reloading configuration: {str(e)}"
            )
        ]


async def handle_setup_elasticsearch(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle setup_elasticsearch tool."""
    try:
        include_kibana = arguments.get("include_kibana", True)
        force_recreate = arguments.get("force_recreate", False)
        
        # Get config path
        config_path = Path(__file__).parent / "config.json"
        config = load_config()
        
        if force_recreate:
            # Stop existing containers first
            setup = ElasticsearchSetup(config_path)
            stop_result = setup.stop_containers()
            
            # Wait a bit for containers to stop
            import time
            time.sleep(5)
        
        # Run auto setup
        result = auto_setup_elasticsearch(config_path, config)
        
        if result["status"] == "already_configured":
            return [
                types.TextContent(
                    type="text",
                    text=f"✅ Elasticsearch is already configured and running at {result['host']}:{result['port']}"
                )
            ]
        elif result["status"] == "setup_completed":
            es_info = result["elasticsearch"]
            kibana_info = result.get("kibana")
            
            message = f"🎉 Elasticsearch setup completed!\n"
            message += f"📍 Elasticsearch: http://{es_info['host']}:{es_info['port']}\n"
            
            if kibana_info and kibana_info.get("status") in ["running", "already_running"]:
                message += f"📊 Kibana: http://{kibana_info['host']}:{kibana_info['port']}\n"
            elif kibana_info and "error" in kibana_info:
                message += f"⚠️  Kibana setup failed: {kibana_info['error']}\n"
            
            message += "\n💡 Configuration has been updated automatically."
            
            # Reload configuration in current session
            new_config = load_config()
            init_elasticsearch(new_config)
            reset_es_client()
            
            return [
                types.TextContent(
                    type="text",
                    text=message
                )
            ]
        else:
            error_msg = result.get("error", "Unknown error")
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Failed to setup Elasticsearch: {error_msg}"
                )
            ]
            
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error setting up Elasticsearch: {str(e)}"
            )
        ]


async def handle_elasticsearch_status(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle elasticsearch_status tool."""
    try:
        config_path = Path(__file__).parent / "config.json"
        setup = ElasticsearchSetup(config_path)
        
        status = setup.get_container_status()
        
        if "error" in status:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error checking container status: {status['error']}"
                )
            ]
        
        message = "📊 Elasticsearch & Kibana Container Status:\n\n"
        
        # Elasticsearch status
        es_status = status["elasticsearch"]
        message += f"🔍 Elasticsearch ({es_status['container_name']}):\n"
        message += f"  - Exists: {'✅' if es_status['exists'] else '❌'}\n"
        message += f"  - Running: {'✅' if es_status['running'] else '❌'}\n"
        
        if es_status['running']:
            message += f"  - URL: http://localhost:9200\n"
        
        message += "\n"
        
        # Kibana status
        kibana_status = status["kibana"]
        message += f"📊 Kibana ({kibana_status['container_name']}):\n"
        message += f"  - Exists: {'✅' if kibana_status['exists'] else '❌'}\n"
        message += f"  - Running: {'✅' if kibana_status['running'] else '❌'}\n"
        
        if kibana_status['running']:
            message += f"  - URL: http://localhost:5601\n"
        
        # Current config
        config = load_config()
        message += f"\n⚙️ Current Configuration:\n"
        message += f"  - Host: {config['elasticsearch']['host']}\n"
        message += f"  - Port: {config['elasticsearch']['port']}\n"
        
        return [
            types.TextContent(
                type="text",
                text=message
            )
        ]
        
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error checking Elasticsearch status: {str(e)}"
            )
        ]
