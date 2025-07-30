"""
Elasticsearch tool handlers.
"""
import json
from typing import List, Dict, Any, Optional

import mcp.types as types
from .elasticsearch_client import get_es_client
from .document_schema import (
    validate_document_structure, 
    DocumentValidationError, 
    create_document_template,
    format_validation_error
)
from .config import load_config


async def handle_search(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle search tool."""
    es = get_es_client()
    
    index = arguments.get("index")
    query_text = arguments.get("query")
    size = arguments.get("size", 10)
    fields = arguments.get("fields", [])
    
    # Build search query
    search_body = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["title^3", "summary^2", "content", "tags^2", "features^2", "tech_stack^2"]
            }
        },
        "size": size
    }
    
    if fields:
        search_body["_source"] = fields
    
    result = es.search(index=index, body=search_body)
    
    # Format results
    formatted_results = []
    for hit in result['hits']['hits']:
        source = hit['_source']
        score = hit['_score']
        formatted_results.append({
            "id": hit['_id'],
            "score": score,
            "source": source
        })
    
    return [
        types.TextContent(
            type="text",
            text=f"Search results for '{query_text}' in index '{index}':\n\n" +
                 json.dumps({
                     "total": result['hits']['total']['value'],
                     "results": formatted_results
                 }, indent=2, ensure_ascii=False)
        )
    ]


async def handle_index_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle index_document tool with document validation."""
    es = get_es_client()
    
    index = arguments.get("index")
    document = arguments.get("document")
    doc_id = arguments.get("doc_id")
    validate_schema = arguments.get("validate_schema", True)  # Default to True
    
    # Validate document structure if requested
    if validate_schema:
        try:
            # Get base directory from config
            config = load_config()
            base_directory = config.get("security", {}).get("allowed_base_directory")
            
            # Check if this looks like a knowledge base document
            if isinstance(document, dict) and "id" in document and "title" in document:
                validated_doc = validate_document_structure(document, base_directory)
                document = validated_doc
                
                # Use the document ID from the validated document if not provided
                if not doc_id:
                    doc_id = document.get("id")
                    
                return [
                    types.TextContent(
                        type="text",
                        text=f"✅ Document validation passed. Structure is correct.\n"
                             f"Document ID: {doc_id}\n"
                             f"Title: {document.get('title')}\n"
                             f"Priority: {document.get('priority')}\n"
                             f"Tags: {document.get('tags')}\n"
                             f"Source Type: {document.get('source_type')}\n\n"
                             f"Ready to index to '{index}' index."
                    )
                ]
            else:
                # For non-knowledge base documents, still validate with strict mode if enabled
                validated_doc = validate_document_structure(document, base_directory, is_knowledge_doc=False)
                document = validated_doc
        except DocumentValidationError as e:
            return [
                types.TextContent(
                    type="text",
                    text=format_validation_error(e)
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Validation error: {str(e)}"
                )
            ]
    
    # Index the document
    try:
        if doc_id:
            result = es.index(index=index, id=doc_id, body=document)
        else:
            result = es.index(index=index, body=document)
        
        return [
            types.TextContent(
                type="text",
                text=f"Document indexed successfully:\n{json.dumps(result, indent=2)}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Failed to index document: {str(e)}"
            )
        ]


async def handle_create_index(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle create_index tool."""
    es = get_es_client()
    
    index = arguments.get("index")
    mapping = arguments.get("mapping")
    settings = arguments.get("settings", {})
    
    body = {"mappings": mapping}
    if settings:
        body["settings"] = settings
    
    result = es.indices.create(index=index, body=body)
    
    return [
        types.TextContent(
            type="text",
            text=f"Index '{index}' created successfully:\n{json.dumps(result, indent=2)}"
        )
    ]


async def handle_get_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_document tool."""
    es = get_es_client()
    
    index = arguments.get("index")
    doc_id = arguments.get("doc_id")
    
    result = es.get(index=index, id=doc_id)
    
    return [
        types.TextContent(
            type="text",
            text=f"Document retrieved:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
        )
    ]


async def handle_delete_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_document tool."""
    es = get_es_client()
    
    index = arguments.get("index")
    doc_id = arguments.get("doc_id")
    
    result = es.delete(index=index, id=doc_id)
    
    return [
        types.TextContent(
            type="text",
            text=f"Document deleted:\n{json.dumps(result, indent=2)}"
        )
    ]


async def handle_list_indices(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle list_indices tool."""
    es = get_es_client()
    
    indices = es.indices.get_alias(index="*")
    
    # Get stats for each index
    indices_info = []
    for index_name in indices.keys():
        if not index_name.startswith('.'):  # Skip system indices
            try:
                stats = es.indices.stats(index=index_name)
                doc_count = stats['indices'][index_name]['total']['docs']['count']
                size = stats['indices'][index_name]['total']['store']['size_in_bytes']
                indices_info.append({
                    "name": index_name,
                    "docs": doc_count,
                    "size_bytes": size
                })
            except:
                indices_info.append({
                    "name": index_name,
                    "docs": "unknown",
                    "size_bytes": "unknown"
                })
    
    return [
        types.TextContent(
            type="text",
            text=f"Available indices:\n{json.dumps(indices_info, indent=2)}"
        )
    ]


async def handle_delete_index(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_index tool."""
    es = get_es_client()
    
    index = arguments.get("index")
    
    result = es.indices.delete(index=index)
    
    return [
        types.TextContent(
            type="text",
            text=f"Index '{index}' deleted successfully:\n{json.dumps(result, indent=2)}"
        )
    ]


async def handle_validate_document_schema(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle validate_document_schema tool."""
    document = arguments.get("document")
    
    try:
        # Get base directory from config
        config = load_config()
        base_directory = config.get("security", {}).get("allowed_base_directory")
        
        validated_doc = validate_document_structure(document, base_directory)
        return [
            types.TextContent(
                type="text",
                text=f"✅ Document validation successful!\n\n"
                     f"Validated document:\n{json.dumps(validated_doc, indent=2, ensure_ascii=False)}\n\n"
                     f"Document is ready to be indexed."
            )
        ]
    except DocumentValidationError as e:
        return [
            types.TextContent(
                type="text",
                text=format_validation_error(e)
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Validation error: {str(e)}"
            )
        ]


async def handle_create_document_template(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle create_document_template tool."""
    try:
        # Get base directory from config
        config = load_config()
        base_directory = config.get("security", {}).get("allowed_base_directory")
        
        title = arguments.get("title")
        file_path = arguments.get("file_path") 
        priority = arguments.get("priority", "medium")
        source_type = arguments.get("source_type", "markdown")
        tags = arguments.get("tags", [])
        summary = arguments.get("summary", "")
        key_points = arguments.get("key_points", [])
        related = arguments.get("related", [])
        
        template = create_document_template(
            title=title,
            file_path=file_path,
            priority=priority,
            source_type=source_type,
            tags=tags,
            summary=summary,
            key_points=key_points,
            related=related,
            base_directory=base_directory
        )
        
        return [
            types.TextContent(
                type="text",
                text=f"✅ Document template created successfully!\n\n"
                     f"{json.dumps(template, indent=2, ensure_ascii=False)}\n\n"
                     f"This template can be used with the 'index_document' tool."
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Failed to create document template: {str(e)}"
            )
        ]
