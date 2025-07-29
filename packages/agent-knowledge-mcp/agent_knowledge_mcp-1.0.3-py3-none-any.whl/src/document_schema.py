"""
Document schema validation for knowledge base documents.
"""
import json
import re
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Document schema definition
DOCUMENT_SCHEMA = {
    "required_fields": [
        "id", "title", "summary", "file_path", "file_name", 
        "directory", "last_modified", "priority", "tags", 
        "related", "source_type", "key_points"
    ],
    "field_types": {
        "id": str,
        "title": str,
        "summary": str,
        "file_path": str,
        "file_name": str,
        "directory": str,
        "last_modified": str,
        "priority": str,
        "tags": list,
        "related": list,
        "source_type": str,
        "key_points": list
    },
    "priority_values": ["high", "medium", "low"],
    "source_types": ["markdown", "code", "config", "documentation", "tutorial"],
}

class DocumentValidationError(Exception):
    """Exception raised when document validation fails."""
    pass

def load_validation_config() -> Dict[str, Any]:
    """
    Load validation configuration from config.json.
    
    Returns:
        Validation configuration dict
    """
    try:
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("document_validation", {
                    "strict_schema_validation": False,
                    "allow_extra_fields": True,
                    "required_fields_only": False,
                    "auto_correct_paths": True
                })
    except Exception as e:
        print(f"⚠️  Warning: Could not load validation config: {e}")
    
    # Default fallback
    return {
        "strict_schema_validation": False,
        "allow_extra_fields": True,
        "required_fields_only": False,
        "auto_correct_paths": True
    }

def normalize_file_path(file_path: str, base_directory: str = None) -> Dict[str, str]:
    """
    Normalize file path to relative format and extract components.
    
    Args:
        file_path: Input file path (absolute or relative)
        base_directory: Base directory for relative paths
        
    Returns:
        Dict with normalized paths
        
    Raises:
        ValueError: If file_path is empty or invalid
    """
    if not file_path or not file_path.strip():
        raise ValueError("File path cannot be empty")
    
    # Convert backslashes to forward slashes for consistency
    file_path = file_path.replace('\\', '/')
    path = Path(file_path)
    
    # If absolute path, try to make it relative to base_directory
    if path.is_absolute() and base_directory:
        base_path = Path(base_directory).resolve()
        try:
            # Try to make relative to base directory
            relative_path = path.relative_to(base_path)
            normalized_path = str(relative_path)
            # Convert to forward slashes for consistency
            normalized_path = normalized_path.replace(os.sep, '/')
        except ValueError:
            # If path is not under base directory, keep original but warn
            normalized_path = str(path)
            print(f"⚠️  Warning: Path {file_path} is outside base directory {base_directory}")
    else:
        # Already relative or no base directory
        normalized_path = str(path).replace(os.sep, '/')
        # Remove leading ./ if present
        if normalized_path.startswith('./'):
            normalized_path = normalized_path[2:]
    
    # Extract components using forward slash paths
    path_parts = normalized_path.split('/')
    file_name = path_parts[-1] if path_parts else ""
    directory_parts = path_parts[:-1] if len(path_parts) > 1 else []
    directory = '/'.join(directory_parts) if directory_parts else ""
    
    return {
        "file_path": normalized_path,
        "file_name": file_name,
        "directory": directory
    }

def validate_document_structure(document: Dict[str, Any], base_directory: str = None, is_knowledge_doc: bool = True) -> Dict[str, Any]:
    """
    Validate document structure against schema with strict mode support.
    
    Args:
        document: Document to validate
        base_directory: Base directory for relative path conversion
        is_knowledge_doc: Whether this is a knowledge base document (default: True)
        
    Returns:
        Validated and normalized document
        
    Raises:
        DocumentValidationError: If validation fails
    """
    errors = []
    validation_config = load_validation_config()
    
    # For knowledge base documents, check the full schema
    if is_knowledge_doc:
        # Check for extra fields if strict validation is enabled
        if validation_config.get("strict_schema_validation", False) and not validation_config.get("allow_extra_fields", True):
            allowed_fields = set(DOCUMENT_SCHEMA["required_fields"])
            document_fields = set(document.keys())
            extra_fields = document_fields - allowed_fields
            
            if extra_fields:
                errors.append(f"Extra fields not allowed in strict mode: {', '.join(sorted(extra_fields))}. Allowed fields: {', '.join(sorted(allowed_fields))}")
    else:
        # For non-knowledge documents, only check for extra fields if strict validation is enabled
        if validation_config.get("strict_schema_validation", False) and not validation_config.get("allow_extra_fields", True):
            # For non-knowledge docs, we don't have a predefined schema, so just enforce no extra fields beyond basic ones
            # This is a more lenient check - you might want to customize this based on your needs
            errors.append("Strict schema validation is enabled. Extra fields are not allowed for custom documents.")
    
    # Check required fields only for knowledge base documents
    if is_knowledge_doc:
        required_fields = DOCUMENT_SCHEMA["required_fields"]
        if validation_config.get("required_fields_only", False):
            # Only check fields that are actually required
            for field in required_fields:
                if field not in document:
                    errors.append(f"Missing required field: {field}")
        else:
            # Check all fields in schema
            for field in required_fields:
                if field not in document:
                    errors.append(f"Missing required field: {field}")
    
    if errors:
        raise DocumentValidationError("Validation failed: " + "; ".join(errors))
    
    # For knowledge base documents, perform detailed validation
    if is_knowledge_doc:
        # Validate field types
        for field, expected_type in DOCUMENT_SCHEMA["field_types"].items():
            if field in document:
                if not isinstance(document[field], expected_type):
                    errors.append(f"Field '{field}' must be of type {expected_type.__name__}, got {type(document[field]).__name__}")
        
        # Validate priority values
        if document.get("priority") not in DOCUMENT_SCHEMA["priority_values"]:
            errors.append(f"Priority must be one of {DOCUMENT_SCHEMA['priority_values']}, got '{document.get('priority')}'")
        
        # Validate source_type
        if document.get("source_type") not in DOCUMENT_SCHEMA["source_types"]:
            errors.append(f"Source type must be one of {DOCUMENT_SCHEMA['source_types']}, got '{document.get('source_type')}'")
        
        # Validate ID format (should be alphanumeric with hyphens)
        if document.get("id") and not re.match(r'^[a-zA-Z0-9-_]+$', document["id"]):
            errors.append("ID must contain only alphanumeric characters, hyphens, and underscores")
        
        # Validate timestamp format
        if document.get("last_modified"):
            try:
                datetime.fromisoformat(document["last_modified"].replace('Z', '+00:00'))
            except ValueError:
                errors.append("last_modified must be in ISO 8601 format (e.g., '2025-01-04T10:30:00Z')")
        
        # Validate file_path and normalize if auto_correct_paths is enabled
        if document.get("file_path") and validation_config.get("auto_correct_paths", True):
            # Normalize file path
            path_info = normalize_file_path(document["file_path"], base_directory)
            
            # Update document with normalized paths
            document.update(path_info)
            
            # Validate that file exists (optional warning - file might be created later)
            if base_directory:
                full_path = Path(base_directory) / path_info["file_path"]
                if not full_path.exists():
                    print(f"ℹ️  Info: File {full_path} does not exist yet (will be created)")
        
        # Validate tags (must be non-empty strings)
        if document.get("tags"):
            for i, tag in enumerate(document["tags"]):
                if not isinstance(tag, str) or not tag.strip():
                    errors.append(f"Tag at index {i} must be a non-empty string")
        
        # Validate related documents (must be strings)
        if document.get("related"):
            for i, related_id in enumerate(document["related"]):
                if not isinstance(related_id, str) or not related_id.strip():
                    errors.append(f"Related document ID at index {i} must be a non-empty string")
        
        # Validate key_points (must be non-empty strings)
        if document.get("key_points"):
            for i, point in enumerate(document["key_points"]):
                if not isinstance(point, str) or not point.strip():
                    errors.append(f"Key point at index {i} must be a non-empty string")
    
    if errors:
        raise DocumentValidationError("Validation failed: " + "; ".join(errors))
    
    return document

def generate_document_id(title: str, source_type: str = "markdown") -> str:
    """
    Generate a document ID from title.
    
    Args:
        title: Document title
        source_type: Type of source document
        
    Returns:
        Generated ID
    """
    # Convert title to lowercase, replace spaces with hyphens
    base_id = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    base_id = re.sub(r'\s+', '-', base_id.strip())
    
    # Add source type prefix
    type_prefix = {
        "markdown": "md",
        "code": "code", 
        "config": "cfg",
        "documentation": "doc",
        "tutorial": "tut"
    }.get(source_type, "doc")
    
    return f"{type_prefix}-{base_id}"

def create_document_template(
    title: str,
    file_path: str,
    priority: str = "medium",
    source_type: str = "markdown",
    tags: Optional[List[str]] = None,
    summary: str = "",
    key_points: Optional[List[str]] = None,
    related: Optional[List[str]] = None,
    base_directory: str = None
) -> Dict[str, Any]:
    """
    Create a document template with proper structure.
    
    Args:
        title: Document title
        file_path: Path to the source file
        priority: Priority level (high/medium/low)
        source_type: Type of source
        tags: List of tags
        summary: Brief description
        key_points: List of key points
        related: List of related document IDs
        base_directory: Base directory for path normalization
        
    Returns:
        Properly structured document
    """
    # Normalize file path first
    path_info = normalize_file_path(file_path, base_directory)
    
    document = {
        "id": generate_document_id(title, source_type),
        "title": title,
        "summary": summary or f"Brief description of {title}",
        "file_path": path_info["file_path"],
        "file_name": path_info["file_name"],
        "directory": path_info["directory"],
        "last_modified": datetime.now().isoformat() + "Z",
        "priority": priority,
        "tags": tags or [],
        "related": related or [],
        "source_type": source_type,
        "key_points": key_points or []
    }
    
    return validate_document_structure(document, base_directory)

def format_validation_error(error: DocumentValidationError) -> str:
    """
    Format validation error with a clear example.
    
    Args:
        error: The validation error
        
    Returns:
        Formatted error message with example
    """
    return (
        f"❌ Document validation failed!\n\n{str(error)}\n\n"
        f"Expected format example:\n"
        f"{{\n"
        f'  "id": "auth-jwt-001",\n'
        f'  "title": "JWT Authentication Implementation",\n'
        f'  "summary": "Brief description of the document",\n'
        f'  "file_path": "auth/jwt.md",\n'
        f'  "file_name": "jwt.md",\n'
        f'  "directory": "auth",\n'
        f'  "last_modified": "2025-01-04T10:30:00Z",\n'
        f'  "priority": "high",\n'
        f'  "tags": ["tag1", "tag2"],\n'
        f'  "related": ["related-doc-id"],\n'
        f'  "source_type": "markdown",\n'
        f'  "key_points": ["Key point 1", "Key point 2"]\n'
        f"}}"
    )


def get_example_document() -> Dict[str, Any]:
    """
    Generate an example document with proper format.
    
    Args:
        context: Context for the example (general, jwt, api, config, etc.)
        
    Returns:
        Example document structure
    """
    examples = {
            "id": "doc-example-document",
            "title": "Example Document",
            "summary": "Brief description of the document content",
            "file_path": "docs/example.md",
            "file_name": "example.md",
            "directory": "docs",
            "last_modified": "2025-07-04T16:00:00Z",
            "priority": "medium",
            "tags": ["example", "template"],
            "related": [],
            "source_type": "markdown",
            "key_points": ["Key point 1", "Key point 2"]
    }

    return examples


def format_validation_error(error: DocumentValidationError, context: str = "general") -> str:
    """
    Format validation error with example and requirements.
    
    Args:
        error: The validation error
        context: Context for example selection
        
    Returns:
        Formatted error message with example
    """
    example_doc = get_example_document(context)
    
    error_message = f"❌ Document validation failed!\n\n{str(error)}\n\n"
    error_message += "📋 Required fields and format:\n"
    
    # Show requirements
    error_message += f"• Required fields: {', '.join(DOCUMENT_SCHEMA['required_fields'])}\n"
    error_message += f"• Priority values: {', '.join(DOCUMENT_SCHEMA['priority_values'])}\n"
    error_message += f"• Source types: {', '.join(DOCUMENT_SCHEMA['source_types'])}\n"
    error_message += f"• ID format: alphanumeric, hyphens, underscores only\n"
    error_message += f"• Timestamp format: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)\n\n"
    
    # Show example
    error_message += "📄 Example document format:\n"
    error_message += json.dumps(example_doc, indent=2, ensure_ascii=False)
    
    return error_message
