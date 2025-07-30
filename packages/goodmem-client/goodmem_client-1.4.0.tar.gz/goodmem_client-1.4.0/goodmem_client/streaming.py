# coding: utf-8

"""
Streaming client for GoodMem API

This module provides a convenient streaming interface for the GoodMem memory retrieval API,
handling both SSE (Server-Sent Events) and NDJSON streaming formats.
"""

import json
import logging
import re
from typing import Any, Dict, Generator, List, Optional, Union
from urllib.parse import urlencode

import urllib3
from pydantic import BaseModel, Field

from goodmem_client.api.memories_api import MemoriesApi
from goodmem_client.api_client import ApiClient
from goodmem_client.models.memory import Memory


class AbstractReply(BaseModel):
    """Generated abstractive reply with relevance information"""
    text: str = Field(description="Generated abstractive reply text")
    relevance_score: float = Field(description="Relevance score for this reply (0.0 to 1.0)", alias="relevanceScore")
    result_set_id: Optional[str] = Field(default=None, description="Optional link to a specific result set", alias="resultSetId")


class ChunkReference(BaseModel):
    """Reference to a memory chunk with pointer to its parent memory"""
    result_set_id: str = Field(description="Result set ID that produced this chunk", alias="resultSetId")
    chunk: Dict[str, Any] = Field(description="The memory chunk data")
    memory_index: int = Field(description="Index of the chunk's memory in the client's memories array", alias="memoryIndex")
    relevance_score: float = Field(description="Relevance score for this chunk (0.0 to 1.0)", alias="relevanceScore")


class RetrievedItem(BaseModel):
    """A retrieved result that can be either a Memory or MemoryChunk"""
    memory: Optional[Dict[str, Any]] = Field(default=None, description="Complete memory object (if retrieved)")
    chunk: Optional[ChunkReference] = Field(default=None, description="Reference to a memory chunk (if retrieved)")


class ResultSetBoundary(BaseModel):
    """Marks the BEGIN/END of a logical result set (e.g. vector match, rerank)"""
    result_set_id: str = Field(description="Unique result set ID (UUID)", alias="resultSetId")
    kind: str = Field(description="Boundary type: 'BEGIN' or 'END'")
    stage_name: str = Field(description="Free-form stage label for logging", alias="stageName")
    expected_items: Optional[int] = Field(default=None, description="Hint for progress bars", alias="expectedItems")


class GoodMemStatus(BaseModel):
    """Warning or non-fatal status with granular codes (operation continues)"""
    code: str = Field(description="Status code for the warning or informational message")
    message: str = Field(description="Human-readable status message")


class RetrieveMemoryEvent(BaseModel):
    """Streaming event from memory retrieval operation"""
    result_set_boundary: Optional[ResultSetBoundary] = Field(default=None, description="Result set boundary marker", alias="resultSetBoundary")
    retrieved_item: Optional[RetrievedItem] = Field(default=None, description="A retrieved memory or chunk", alias="retrievedItem")
    abstract_reply: Optional[AbstractReply] = Field(default=None, description="Generated abstractive reply", alias="abstractReply")
    memory_definition: Optional[Dict[str, Any]] = Field(default=None, description="Memory object to add to client's memories array", alias="memoryDefinition")
    status: Optional[GoodMemStatus] = Field(default=None, description="Warning or non-fatal status message")


class MemoryStreamClient:
    """
    Streaming client for memory retrieval operations.
    
    This client provides a convenient Python interface for consuming streaming
    memory retrieval results from the GoodMem API.
    """
    
    def __init__(self, api_client: Optional[ApiClient] = None):
        """
        Initialize the streaming client.
        
        Args:
            api_client: Optional ApiClient instance. If None, uses the default.
        """
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client
        self.memories_api = MemoriesApi(api_client)
    
    def retrieve_memory_stream(
        self,
        message: str,
        space_ids: Optional[List[str]] = None,
        requested_size: Optional[int] = None,
        fetch_memory: Optional[bool] = None,
        fetch_memory_content: Optional[bool] = None,
        generate_abstract: Optional[bool] = None,
        format: str = "ndjson"
    ) -> Generator[RetrieveMemoryEvent, None, None]:
        """
        Stream semantic memory retrieval results.
        
        Args:
            message: Primary query/message for semantic search
            space_ids: List of space UUIDs to search within
            requested_size: Maximum number of memories to retrieve
            fetch_memory: Whether to fetch memory definitions (defaults to true)
            fetch_memory_content: Whether to fetch original content for memories (defaults to false)
            generate_abstract: Whether to generate an abstract summary (defaults to true)
            format: Streaming format - either "ndjson" or "sse" (default: "ndjson")
        
        Yields:
            RetrieveMemoryEvent: Parsed streaming events
            
        Raises:
            ValueError: If format is not "ndjson" or "sse"
            Exception: If API request fails
        """
        if format not in ("ndjson", "sse"):
            raise ValueError("format must be either 'ndjson' or 'sse'")
        
        # Build query parameters
        params = {"message": message}
        if space_ids:
            params["spaceIds"] = ",".join(space_ids)
        if requested_size is not None:
            params["requestedSize"] = str(requested_size)
        if fetch_memory is not None:
            params["fetchMemory"] = str(fetch_memory).lower()
        if fetch_memory_content is not None:
            params["fetchMemoryContent"] = str(fetch_memory_content).lower()
        if generate_abstract is not None:
            params["generateAbstract"] = str(generate_abstract).lower()
        
        # Set appropriate Accept header
        accept_header = "application/x-ndjson" if format == "ndjson" else "text/event-stream"
        
        # Build the URL
        host = self.api_client.configuration.host
        url = f"{host}/v1/memories:retrieve?{urlencode(params)}"
        
        # Get authentication headers
        headers = {"Accept": accept_header}
        
        # Add API key from default headers (set by add_auth_headers in common.py)
        if hasattr(self.api_client, 'default_headers') and 'x-api-key' in self.api_client.default_headers:
            headers['x-api-key'] = self.api_client.default_headers['x-api-key']
        
        # Make the streaming request
        http = urllib3.PoolManager()
        response = http.request("GET", url, headers=headers, preload_content=False)
        
        if response.status != 200:
            error_data = response.read().decode('utf-8')
            raise Exception(f"API request failed with status {response.status}: {error_data}")
        
        try:
            if format == "ndjson":
                yield from self._parse_ndjson_stream(response)
            else:
                yield from self._parse_sse_stream(response)
        finally:
            response.close()
    
    def _parse_ndjson_stream(self, response) -> Generator[RetrieveMemoryEvent, None, None]:
        """Parse NDJSON streaming response."""
        buffer = ""
        
        for chunk_bytes in response.stream(1024):
            if not chunk_bytes:
                continue
            
            try:
                buffer += chunk_bytes.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                # Skip chunks with encoding issues
                continue
            
            # Process complete lines (JSON objects separated by newlines)
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                
                if not line:
                    continue
                    
                try:
                    event_data = json.loads(line)
                    event = RetrieveMemoryEvent.model_validate(event_data)
                    yield event
                except json.JSONDecodeError as e:
                    logging.debug(f"Failed to parse NDJSON line: {e}. Line content: {line[:100]}{'...' if len(line) > 100 else ''}")
                    continue
                except Exception as e:
                    logging.debug(f"Failed to validate NDJSON event: {e}. Line content: {line[:100]}{'...' if len(line) > 100 else ''}")
                    continue
    
    def _parse_sse_stream(self, response) -> Generator[RetrieveMemoryEvent, None, None]:
        """Parse Server-Sent Events streaming response."""
        buffer = ""
        
        for chunk_bytes in response.stream(1024):
            if not chunk_bytes:
                continue
                
            try:
                buffer += chunk_bytes.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                # Skip chunks with encoding issues
                continue
            
            # Process complete SSE events
            while '\n\n' in buffer:
                event_text, buffer = buffer.split('\n\n', 1)
                event = self._parse_sse_event(event_text)
                if event:
                    yield event
    
    def _parse_sse_event(self, event_text: str) -> Optional[RetrieveMemoryEvent]:
        """Parse a single SSE event."""
        lines = event_text.strip().split('\n')
        event_type = None
        data = None
        
        for line in lines:
            if line.startswith('event:'):
                event_type = line[6:].strip()
            elif line.startswith('data:'):
                data = line[5:].strip()
        
        # Skip close events and events without data
        if event_type == "close" or not data:
            return None
            
        try:
            event_data = json.loads(data)
            return RetrieveMemoryEvent.model_validate(event_data)
        except (json.JSONDecodeError, Exception):
            return None


# Convenience function for easy access
def create_stream_client(api_client: Optional[ApiClient] = None) -> MemoryStreamClient:
    """
    Create a new MemoryStreamClient instance.
    
    Args:
        api_client: Optional ApiClient instance. If None, uses the default.
        
    Returns:
        MemoryStreamClient: New streaming client instance
    """
    return MemoryStreamClient(api_client)