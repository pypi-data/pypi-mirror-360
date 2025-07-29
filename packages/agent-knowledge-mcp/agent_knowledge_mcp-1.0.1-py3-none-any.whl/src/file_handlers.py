"""
File system tool handlers.
"""
import json
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any

import mcp.types as types
from .security import get_safe_path, is_path_allowed, get_allowed_base_dir


async def handle_read_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle read_file tool."""
    file_path = arguments.get("file_path")
    encoding = arguments.get("encoding", "utf-8")
    
    try:
        path_obj = get_safe_path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path_obj, 'r', encoding=encoding) as f:
            content = f.read()
        
        return [
            types.TextContent(
                type="text",
                text=f"Content of '{file_path}':\n\n{content}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error reading file '{file_path}': {str(e)}"
            )
        ]


async def handle_write_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle write_file tool."""
    file_path = arguments.get("file_path")
    content = arguments.get("content")
    encoding = arguments.get("encoding", "utf-8")
    create_dirs = arguments.get("create_dirs", True)
    
    try:
        path_obj = get_safe_path(file_path)
        
        if create_dirs:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path_obj, 'w', encoding=encoding) as f:
            f.write(content)
        
        return [
            types.TextContent(
                type="text",
                text=f"File '{file_path}' written successfully. Size: {len(content)} characters."
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error writing file '{file_path}': {str(e)}"
            )
        ]


async def handle_append_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle append_file tool."""
    file_path = arguments.get("file_path")
    content = arguments.get("content")
    encoding = arguments.get("encoding", "utf-8")
    
    try:
        path_obj = get_safe_path(file_path)
        
        with open(path_obj, 'a', encoding=encoding) as f:
            f.write(content)
        
        return [
            types.TextContent(
                type="text",
                text=f"Content appended to '{file_path}' successfully. Added: {len(content)} characters."
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error appending to file '{file_path}': {str(e)}"
            )
        ]


async def handle_delete_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_file tool."""
    file_path = arguments.get("file_path")
    
    try:
        path_obj = get_safe_path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path_obj.is_file():
            path_obj.unlink()
            return [
                types.TextContent(
                    type="text",
                    text=f"File '{file_path}' deleted successfully."
                )
            ]
        else:
            raise IsADirectoryError(f"'{file_path}' is a directory, not a file.")
            
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error deleting file '{file_path}': {str(e)}"
            )
        ]


async def handle_move_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle move_file tool."""
    source_path = arguments.get("source_path")
    destination_path = arguments.get("destination_path")
    create_dirs = arguments.get("create_dirs", True)
    
    try:
        source_obj = get_safe_path(source_path)
        dest_obj = get_safe_path(destination_path)
        
        if not source_obj.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if create_dirs:
            dest_obj.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source_obj), str(dest_obj))
        
        return [
            types.TextContent(
                type="text",
                text=f"File moved successfully from '{source_path}' to '{destination_path}'"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error moving file from '{source_path}' to '{destination_path}': {str(e)}"
            )
        ]


async def handle_copy_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle copy_file tool."""
    source_path = arguments.get("source_path")
    destination_path = arguments.get("destination_path")
    create_dirs = arguments.get("create_dirs", True)
    
    try:
        source_obj = get_safe_path(source_path)
        dest_obj = get_safe_path(destination_path)
        
        if not source_obj.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if create_dirs:
            dest_obj.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(str(source_obj), str(dest_obj))
        
        return [
            types.TextContent(
                type="text",
                text=f"File copied successfully from '{source_path}' to '{destination_path}'"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error copying file from '{source_path}' to '{destination_path}': {str(e)}"
            )
        ]


async def handle_list_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle list_directory tool."""
    directory_path = arguments.get("directory_path")
    include_hidden = arguments.get("include_hidden", False)
    recursive = arguments.get("recursive", False)
    
    try:
        path_obj = get_safe_path(directory_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not path_obj.is_dir():
            raise NotADirectoryError(f"'{directory_path}' is not a directory")
        
        items = []
        
        if recursive:
            pattern = "**/*" if include_hidden else "**/[!.]*"
            for item in path_obj.glob(pattern):
                # Double check each item is still within allowed directory
                if is_path_allowed(str(item)):
                    relative_path = item.relative_to(path_obj)
                    items.append({
                        "name": str(relative_path),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None
                    })
        else:
            for item in path_obj.iterdir():
                if not include_hidden and item.name.startswith('.'):
                    continue
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
        
        return [
            types.TextContent(
                type="text",
                text=f"Contents of '{directory_path}' (limited to {get_allowed_base_dir()}):\n\n{json.dumps(items, indent=2)}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error listing directory '{directory_path}': {str(e)}"
            )
        ]


async def handle_create_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle create_directory tool."""
    directory_path = arguments.get("directory_path")
    parents = arguments.get("parents", True)
    
    try:
        path_obj = get_safe_path(directory_path)
        path_obj.mkdir(parents=parents, exist_ok=False)
        
        return [
            types.TextContent(
                type="text",
                text=f"Directory '{directory_path}' created successfully."
            )
        ]
    except FileExistsError:
        return [
            types.TextContent(
                type="text",
                text=f"Directory '{directory_path}' already exists."
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error creating directory '{directory_path}': {str(e)}"
            )
        ]


async def handle_delete_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_directory tool."""
    directory_path = arguments.get("directory_path")
    recursive = arguments.get("recursive", False)
    
    try:
        path_obj = get_safe_path(directory_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not path_obj.is_dir():
            raise NotADirectoryError(f"'{directory_path}' is not a directory")
        
        # Extra safety: don't allow deleting the base directory itself
        if path_obj.resolve() == get_allowed_base_dir():
            raise ValueError("Cannot delete the base allowed directory")
        
        if recursive:
            shutil.rmtree(str(path_obj))
            message = f"Directory '{directory_path}' and all its contents deleted successfully."
        else:
            path_obj.rmdir()  # Only works if directory is empty
            message = f"Empty directory '{directory_path}' deleted successfully."
        
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
                text=f"Error deleting directory '{directory_path}': {str(e)}"
            )
        ]


async def handle_file_info(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle file_info tool."""
    path = arguments.get("path")
    
    try:
        path_obj = get_safe_path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        stat = path_obj.stat()
        info = {
            "path": str(path_obj.absolute()),
            "name": path_obj.name,
            "type": "directory" if path_obj.is_dir() else "file",
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "permissions": oct(stat.st_mode)[-3:],
            "is_readable": os.access(path_obj, os.R_OK),
            "is_writable": os.access(path_obj, os.W_OK),
            "is_executable": os.access(path_obj, os.X_OK),
            "allowed_base_dir": str(get_allowed_base_dir())
        }
        
        if path_obj.is_file():
            info["extension"] = path_obj.suffix
        
        return [
            types.TextContent(
                type="text",
                text=f"Information for '{path}' (within allowed directory):\n\n{json.dumps(info, indent=2)}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error getting info for '{path}': {str(e)}"
            )
        ]
