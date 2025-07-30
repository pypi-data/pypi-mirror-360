"""
Admin tool handlers.
"""
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

import mcp.types as types
from .config import load_config
from .security import get_allowed_base_dir, set_allowed_base_dir, init_security
from .elasticsearch_client import reset_es_client, init_elasticsearch
from .elasticsearch_setup import auto_setup_elasticsearch, ElasticsearchSetup


async def handle_get_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_config tool."""
    try:
        config = load_config()
        config_str = json.dumps(config, indent=2, ensure_ascii=False)
        
        return [
            types.TextContent(
                type="text",
                text=f"📄 Current configuration:\n\n```json\n{config_str}\n```"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error getting configuration: {str(e)}"
            )
        ]


async def handle_update_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle update_config tool."""
    try:
        config_section = arguments.get("config_section")
        config_key = arguments.get("config_key") 
        config_value = arguments.get("config_value")
        full_config = arguments.get("full_config")
        
        config_path = Path(__file__).parent / "config.json"
        
        if full_config:
            # Update entire config
            if isinstance(full_config, str):
                new_config = json.loads(full_config)
            else:
                new_config = full_config
                
            # Validate new config structure
            required_sections = ["elasticsearch", "security", "document_validation", "version_control", "server"]
            for section in required_sections:
                if section not in new_config:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"❌ Error: Missing required config section '{section}'"
                        )
                    ]
            
            # Write new config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
                
            message = "✅ Full configuration updated successfully!"
            
        elif config_section and config_key is not None:
            # Update specific key
            config = load_config()
            
            if config_section not in config:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ Error: Config section '{config_section}' not found"
                    )
                ]
            
            # Store old value for comparison
            old_value = config[config_section].get(config_key, "<not set>")
            
            # Update the value
            config[config_section][config_key] = config_value
            
            # Write updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            message = f"✅ Configuration updated successfully!\n"
            message += f"Section: {config_section}\n"
            message += f"Key: {config_key}\n"
            message += f"Old value: {old_value}\n"
            message += f"New value: {config_value}"
            
        else:
            return [
                types.TextContent(
                    type="text",
                    text="❌ Error: Must provide either 'full_config' or both 'config_section' and 'config_key'"
                )
            ]
        
        # Reload configuration in current session
        new_config = load_config()
        
        # Reinitialize security if security section was updated
        if (config_section == "security" and config_key == "allowed_base_directory") or full_config:
            init_security(new_config["security"]["allowed_base_directory"])
        
        # Reinitialize Elasticsearch if elasticsearch section was updated
        if (config_section == "elasticsearch") or full_config:
            init_elasticsearch(new_config)
            reset_es_client()
        
        return [
            types.TextContent(
                type="text",
                text=message + f"\n\n💡 Configuration reloaded automatically."
            )
        ]
        
    except json.JSONDecodeError as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error: Invalid JSON format in full_config: {str(e)}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error updating configuration: {str(e)}"
            )
        ]


async def handle_validate_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle validate_config tool."""
    try:
        config_data = arguments.get("config_data")
        
        if isinstance(config_data, str):
            config = json.loads(config_data)
        else:
            config = config_data or load_config()
        
        errors = []
        warnings = []
        
        # Validate structure
        required_sections = ["elasticsearch", "security", "document_validation", "version_control", "server"]
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate elasticsearch section
        if "elasticsearch" in config:
            es_config = config["elasticsearch"]
            if "host" not in es_config:
                errors.append("elasticsearch.host is required")
            if "port" not in es_config:
                errors.append("elasticsearch.port is required")
            elif not isinstance(es_config["port"], int):
                errors.append("elasticsearch.port must be an integer")
        
        # Validate security section
        if "security" in config:
            sec_config = config["security"]
            if "allowed_base_directory" not in sec_config:
                errors.append("security.allowed_base_directory is required")
            else:
                base_dir = Path(sec_config["allowed_base_directory"])
                if not base_dir.exists():
                    warnings.append(f"security.allowed_base_directory does not exist: {base_dir}")
        
        # Validate document_validation section
        if "document_validation" in config:
            doc_config = config["document_validation"]
            bool_fields = ["strict_schema_validation", "allow_extra_fields", "required_fields_only", "auto_correct_paths"]
            for field in bool_fields:
                if field in doc_config and not isinstance(doc_config[field], bool):
                    errors.append(f"document_validation.{field} must be a boolean")
        
        # Validate version_control section
        if "version_control" in config:
            vc_config = config["version_control"]
            if "enabled" in vc_config and not isinstance(vc_config["enabled"], bool):
                errors.append("version_control.enabled must be a boolean")
            if "type" in vc_config and vc_config["type"] not in ["git", "svn"]:
                errors.append("version_control.type must be 'git' or 'svn'")
        
        # Prepare result message
        if errors:
            message = f"❌ Configuration validation failed!\n\nErrors:\n"
            for error in errors:
                message += f"  • {error}\n"
        else:
            message = "✅ Configuration validation passed!"
        
        if warnings:
            message += f"\n⚠️  Warnings:\n"
            for warning in warnings:
                message += f"  • {warning}\n"
        
        # Show current validation settings
        if "document_validation" in config:
            doc_val = config["document_validation"]
            message += f"\n📋 Current document validation settings:\n"
            message += f"  • Strict schema validation: {doc_val.get('strict_schema_validation', False)}\n"
            message += f"  • Allow extra fields: {doc_val.get('allow_extra_fields', True)}\n"
            message += f"  • Required fields only: {doc_val.get('required_fields_only', False)}\n"
            message += f"  • Auto correct paths: {doc_val.get('auto_correct_paths', True)}\n"
        
        return [
            types.TextContent(
                type="text",
                text=message
            )
        ]
        
    except json.JSONDecodeError as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error: Invalid JSON format: {str(e)}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error validating configuration: {str(e)}"
            )
        ]


# Keep backward compatibility
async def handle_get_allowed_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_allowed_directory tool (deprecated - use get_config instead)."""
    return [
        types.TextContent(
            type="text",
            text=f"⚠️  Note: This tool is deprecated. Use 'get_config' instead.\n\nCurrent allowed base directory: {get_allowed_base_dir()}"
        )
    ]


async def handle_set_allowed_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle set_allowed_directory tool (deprecated - use update_config instead)."""
    directory_path = arguments.get("directory_path")
    
    try:
        new_path = Path(directory_path).resolve()
        
        if not new_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not new_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory_path}")
        
        # Use the new update_config approach
        result = await handle_update_config({
            "config_section": "security",
            "config_key": "allowed_base_directory",
            "config_value": str(new_path)
        })
        
        return [
            types.TextContent(
                type="text",
                text=f"⚠️  Note: This tool is deprecated. Use 'update_config' instead.\n\n{result[0].text}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error setting allowed directory to '{directory_path}': {str(e)}\n\n💡 Consider using 'update_config' tool instead."
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


async def handle_server_status(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle server_status tool - check server status, version and updates."""
    try:
        check_updates = arguments.get("check_updates", True)
        
        # Get current version
        current_version = "unknown"
        try:
            # When running from uvx package, use standard import
            try:
                import importlib.metadata
                current_version = importlib.metadata.version("agent-knowledge-mcp")
            except:
                # Fallback to local import (for development)
                try:
                    from . import __version__ as current_version
                except ImportError:
                    try:
                        from src import __version__ as current_version
                    except ImportError:
                        # Last resort - fallback
                        pass
        except Exception:
            pass
        
        # Get server status
        config = load_config()
        server_status = "running"
        
        # Check installation method
        installation_method = "unknown"
        try:
            # Check if installed via uvx
            result = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and "agent-knowledge-mcp" in result.stdout:
                installation_method = "uvx"
        except:
            pass
        
        # Check for updates if requested
        latest_version = None
        update_available = False
        recommendation = ""
        
        if check_updates and installation_method == "uvx":
            try:
                import requests
                response = requests.get(
                    "https://pypi.org/pypi/agent-knowledge-mcp/json",
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data["info"]["version"]
                    
                    # Simple version comparison (works for semver)
                    if latest_version != current_version:
                        update_available = True
                        recommendation = f"🔄 New version {latest_version} available! Use 'server_upgrade' to update."
            except Exception as e:
                latest_version = f"Error checking: {str(e)}"
        
        # Build status message
        message = f"🖥️  Server Status Report:\n\n"
        message += f"📍 Current Version: {current_version}\n"
        
        if latest_version:
            message += f"📦 Latest Version: {latest_version}\n"
        
        message += f"🔧 Installation Method: {installation_method}\n"
        message += f"⚡ Server Status: {server_status}\n"
        message += f"🗂️  Elasticsearch: {config['elasticsearch']['host']}:{config['elasticsearch']['port']}\n"
        
        if update_available:
            message += f"\n✨ {recommendation}\n"
        elif check_updates and latest_version and not update_available:
            message += f"\n✅ You are running the latest version!\n"
        
        if installation_method != "uvx":
            message += f"\n💡 Note: Server management tools only work with uvx installation.\n"
            message += f"   Install via: uvx install agent-knowledge-mcp\n"
        
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
                text=f"❌ Error checking server status: {str(e)}"
            )
        ]


async def handle_server_upgrade(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle server_upgrade tool - clean uv cache and instruct user to reload client."""
    try:
        # Check if uv is available
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return [
                types.TextContent(
                    type="text",
                    text="❌ Error: uv is not installed or not available in PATH.\n\n"
                         "Please install uv first."
                )
            ]
        
        # Check if this package is installed via uvx
        try:
            list_result = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "agent-knowledge-mcp" not in list_result.stdout:
                return [
                    types.TextContent(
                        type="text",
                        text="⚠️ Agent Knowledge MCP server is not installed via uv tool.\n\n"
                             "This tool only works when the server was installed using:\n"
                             "uv tool install agent-knowledge-mcp\n\n"
                             f"Current uv tool packages:\n{list_result.stdout.strip() or 'None'}"
                    )
                ]
        except:
            return [
                types.TextContent(
                    type="text",
                    text="⚠️ Cannot verify uvx installation. Please ensure agent-knowledge-mcp is installed via uvx."
                )
            ]
        
        # Clean uv cache to ensure fresh package download on next run
        print("Cleaning uv cache...")
        result = subprocess.run(
            ["uv", "cache", "clean"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            message = f"🧹 UV cache cleaned successfully!\n\n"
            message += f"🔄 To upgrade Agent Knowledge MCP server:\n\n"
            message += f"1. **Restart your MCP client:**\n"
            message += f"   • VS Code: Reload window (Ctrl/Cmd + Shift + P → 'Reload Window')\n"
            message += f"   • Claude Desktop: Restart the application\n"
            message += f"   • Other clients: Restart/reload the client\n\n"
            message += f"2. **The client will automatically download the latest version** from PyPI\n\n"
            message += f"✨ Cache cleared! Next client restart will fetch the latest version.\n\n"
            
            if result.stdout.strip():
                message += f"Cache clean output:\n{result.stdout.strip()}\n\n"
            
            message += f"� Note: uvx doesn't have an 'upgrade' command, so we clean the cache\n"
            message += f"and let the client fetch the latest version on next restart."
            
            return [
                types.TextContent(
                    type="text",
                    text=message
                )
            ]
        else:
            error_msg = f"❌ Failed to clean uv cache\n\n"
            error_msg += f"Return code: {result.returncode}\n"
            if result.stderr.strip():
                error_msg += f"Error output:\n{result.stderr.strip()}\n"
            if result.stdout.strip():
                error_msg += f"Standard output:\n{result.stdout.strip()}\n"
            
            error_msg += f"\n💡 You can manually restart your MCP client to check for updates."
            
            return [
                types.TextContent(
                    type="text",
                    text=error_msg
                )
            ]
            
    except subprocess.TimeoutExpired:
        return [
            types.TextContent(
                type="text",
                text="❌ Timeout: Cache clean took too long. Please try again."
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error during upgrade process: {str(e)}\n\n"
                     f"💡 You can manually restart your MCP client to check for updates."
            )
        ]
