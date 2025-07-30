"""
Tool definitions for Elasticsearch MCP Server.
"""
import mcp.types as types
from typing import List


def get_elasticsearch_tools() -> List[types.Tool]:
    """Get list of Elasticsearch tools."""
    return [
        types.Tool(
            name="search",
            description="Search documents in Elasticsearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name to search in"},
                    "query": {"type": "string", "description": "Search query text"},
                    "size": {"type": "integer", "description": "Number of results to return", "default": 10},
                    "fields": {"type": "array", "items": {"type": "string"}, "description": "Specific fields to return"}
                },
                "required": ["index", "query"],
            },
        ),
        types.Tool(
            name="index_document",
            description="Index a document into Elasticsearch with optional schema validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name"},
                    "document": {"type": "object", "description": "Document to index"},
                    "doc_id": {"type": "string", "description": "Document ID (optional)"},
                    "validate_schema": {"type": "boolean", "description": "Validate document structure for knowledge base format", "default": True}
                },
                "required": ["index", "document"],
            },
        ),
        types.Tool(
            name="create_index",
            description="Create a new Elasticsearch index with mapping",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name"},
                    "mapping": {"type": "object", "description": "Index mapping configuration"},
                    "settings": {"type": "object", "description": "Index settings (optional)"}
                },
                "required": ["index", "mapping"],
            },
        ),
        types.Tool(
            name="get_document",
            description="Get a specific document by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name"},
                    "doc_id": {"type": "string", "description": "Document ID"}
                },
                "required": ["index", "doc_id"],
            },
        ),
        types.Tool(
            name="delete_document",
            description="Delete a document by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name"},
                    "doc_id": {"type": "string", "description": "Document ID"}
                },
                "required": ["index", "doc_id"],
            },
        ),
        types.Tool(
            name="list_indices",
            description="List all Elasticsearch indices",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="delete_index",
            description="Delete an Elasticsearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name to delete"}
                },
                "required": ["index"],
            },
        ),
        types.Tool(
            name="validate_document_schema",
            description="Validate document structure against knowledge base schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "Document to validate"}
                },
                "required": ["document"],
            },
        ),
        types.Tool(
            name="create_document_template",
            description="Create a properly structured document template for knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "file_path": {"type": "string", "description": "Path to the source file"},
                    "priority": {"type": "string", "description": "Priority level: high, medium, low", "default": "medium"},
                    "source_type": {"type": "string", "description": "Source type: markdown, code, config, documentation, tutorial", "default": "markdown"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tags"},
                    "summary": {"type": "string", "description": "Brief description"},
                    "key_points": {"type": "array", "items": {"type": "string"}, "description": "List of key points"},
                    "related": {"type": "array", "items": {"type": "string"}, "description": "List of related document IDs"}
                },
                "required": ["title", "file_path"],
            },
        ),
    ]


def get_file_system_tools() -> List[types.Tool]:
    """Get list of file system tools."""
    return [
        types.Tool(
            name="read_file",
            description="Read content from a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to read"},
                    "encoding": {"type": "string", "description": "File encoding (default: utf-8)", "default": "utf-8"}
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="write_file",
            description="Write content to a file (creates new or overwrites existing)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to write"},
                    "content": {"type": "string", "description": "Content to write to the file"},
                    "encoding": {"type": "string", "description": "File encoding (default: utf-8)", "default": "utf-8"},
                    "create_dirs": {"type": "boolean", "description": "Create parent directories if they don't exist", "default": True}
                },
                "required": ["file_path", "content"],
            },
        ),
        types.Tool(
            name="append_file",
            description="Append content to an existing file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to append to"},
                    "content": {"type": "string", "description": "Content to append to the file"},
                    "encoding": {"type": "string", "description": "File encoding (default: utf-8)", "default": "utf-8"}
                },
                "required": ["file_path", "content"],
            },
        ),
        types.Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to delete"}
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="move_file",
            description="Move or rename a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string", "description": "Current path of the file"},
                    "destination_path": {"type": "string", "description": "New path for the file"},
                    "create_dirs": {"type": "boolean", "description": "Create parent directories if they don't exist", "default": True}
                },
                "required": ["source_path", "destination_path"],
            },
        ),
        types.Tool(
            name="copy_file",
            description="Copy a file to a new location",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string", "description": "Path of the file to copy"},
                    "destination_path": {"type": "string", "description": "Path for the copied file"},
                    "create_dirs": {"type": "boolean", "description": "Create parent directories if they don't exist", "default": True}
                },
                "required": ["source_path", "destination_path"],
            },
        ),
        types.Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "Path to the directory to list"},
                    "include_hidden": {"type": "boolean", "description": "Include hidden files/directories", "default": False},
                    "recursive": {"type": "boolean", "description": "List contents recursively", "default": False}
                },
                "required": ["directory_path"],
            },
        ),
        types.Tool(
            name="create_directory",
            description="Create a new directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "Path of the directory to create"},
                    "parents": {"type": "boolean", "description": "Create parent directories if they don't exist", "default": True}
                },
                "required": ["directory_path"],
            },
        ),
        types.Tool(
            name="delete_directory",
            description="Delete a directory (and optionally its contents)",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "Path of the directory to delete"},
                    "recursive": {"type": "boolean", "description": "Delete directory and all its contents", "default": False}
                },
                "required": ["directory_path"],
            },
        ),
        types.Tool(
            name="file_info",
            description="Get information about a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file or directory"}
                },
                "required": ["path"],
            },
        ),
    ]


def get_admin_tools() -> List[types.Tool]:
    """Get list of admin/configuration tools."""
    return [
        # New comprehensive config management tools
        types.Tool(
            name="get_config",
            description="Get the complete configuration from config.json file",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="update_config",
            description="Update the configuration file with new values",
            inputSchema={
                "type": "object",
                "properties": {
                    "config": {
                        "type": "object",
                        "description": "New configuration object to save"
                    }
                },
                "required": ["config"]
            },
        ),
        types.Tool(
            name="validate_config",
            description="Validate a configuration object before saving",
            inputSchema={
                "type": "object",
                "properties": {
                    "config": {
                        "type": "object",
                        "description": "Configuration object to validate"
                    }
                },
                "required": ["config"]
            },
        ),
        
        # Deprecated tools (kept for backward compatibility)
        types.Tool(
            name="get_allowed_directory",
            description="Get the current allowed base directory for file operations (deprecated - use get_config instead)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="set_allowed_directory",
            description="Set the allowed base directory for file operations (deprecated - use update_config instead)",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "New base directory path to allow"}
                },
                "required": ["directory_path"],
            },
        ),
        types.Tool(
            name="reload_config",
            description="Reload configuration from config.json file",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="setup_elasticsearch",
            description="Auto-setup Elasticsearch using Docker if not configured",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_kibana": {"type": "boolean", "description": "Also setup Kibana (default: true)", "default": True},
                    "force_recreate": {"type": "boolean", "description": "Force recreate containers even if they exist", "default": False}
                },
            },
        ),
        types.Tool(
            name="elasticsearch_status",
            description="Check status of Elasticsearch and Kibana containers",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        
        # Server management tools
        types.Tool(
            name="server_status",
            description="Check current server status, version, and available updates",
            inputSchema={
                "type": "object",
                "properties": {
                    "check_updates": {
                        "type": "boolean",
                        "description": "Check for available updates from PyPI",
                        "default": True
                    }
                },
            },
        ),
        types.Tool(
            name="server_upgrade",
            description="Upgrade this MCP server when installed via uvx",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_prompt_guidance",
            description="Get links to GitHub documentation for writing effective prompts with agent-knowledge-mcp",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


def get_version_control_tools() -> List[types.Tool]:
    """Get list of version control tools."""
    return [
        types.Tool(
            name="setup_version_control",
            description="Setup version control (Git or SVN) in knowledge base directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "vcs_type": {
                        "type": "string",
                        "enum": ["git", "svn"],
                        "description": "Version control system to use (git or svn)"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force setup even if VCS already exists",
                        "default": False
                    },
                    "initial_commit": {
                        "type": "boolean", 
                        "description": "Create initial commit with existing files",
                        "default": True
                    }
                },
                "required": []
            },
        ),
        types.Tool(
            name="commit_file",
            description="Commit file changes to version control (Git or SVN)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to file to commit (relative to knowledge base)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message"
                    },
                    "add_if_new": {
                        "type": "boolean",
                        "description": "Add file to VCS if it's not tracked yet",
                        "default": True
                    }
                },
                "required": ["file_path", "message"]
            },
        ),
        types.Tool(
            name="get_previous_file_version",
            description="Get content of file from previous commit",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to file (relative to knowledge base)"
                    },
                    "commits_back": {
                        "type": "integer",
                        "description": "How many commits to go back (1 = previous commit)",
                        "default": 1,
                        "minimum": 1
                    }
                },
                "required": ["file_path"]
            },
        ),
    ]


def get_all_tools() -> List[types.Tool]:
    """Get all available tools."""
    return (
        get_elasticsearch_tools() +
        get_file_system_tools() +
        get_admin_tools() +
        get_version_control_tools()
    )
