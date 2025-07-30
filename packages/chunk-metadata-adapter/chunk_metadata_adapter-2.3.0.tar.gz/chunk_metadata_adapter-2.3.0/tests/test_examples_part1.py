"""
Tests for the examples module (part 1).
"""
import re
import uuid
import pytest
from datetime import datetime, timezone

from chunk_metadata_adapter import (
    SemanticChunk, 
    ChunkType,
    ChunkRole,
    ChunkStatus
)
from chunk_metadata_adapter.examples import (
    example_basic_flat_metadata,
    example_structured_chunk,
    example_conversion_between_formats,
    example_chain_processing
)


class TestExamples:
    """Tests for the examples module functions."""
    
    def test_example_basic_flat_metadata(self):
        """Test the basic flat metadata example."""
        # Run the example
        result = example_basic_flat_metadata()
        
        # Verify the basic structure and fields
        assert isinstance(result, dict)
        assert "uuid" in result
        assert "source_id" in result
        assert "text" in result
        assert "sha256" in result
        assert "created_at" in result
        
        # Verify the type is CodeBlock
        assert result["type"] == "CodeBlock"
        
        # Verify the language is python
        assert result["language"] == "Python"
        
        # Verify the role is developer
        assert result["role"] == "developer"
        
        # Verify the source path
        assert result["source_path"] == "src/hello.py"
        
        # Verify the source lines
        assert result["source_lines_start"] == 10
        assert result["source_lines_end"] == 12
        
        # Verify tags
        assert result["tags"] == "example,hello"
        
        # Verify UUID format
        assert re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            result["uuid"],
            re.IGNORECASE
        )
        
        # Verify ISO datetime format with timezone
        assert re.match(
            r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$',
            result["created_at"]
        )
        
    def test_example_structured_chunk(self):
        """Test the structured chunk example."""
        # Run the example
        result = example_structured_chunk()
        
        # Verify the result is a SemanticChunk
        assert isinstance(result, SemanticChunk)
        
        # Verify the basic properties
        assert result.type == ChunkType.DOC_BLOCK
        assert result.language == "Markdown"
        assert result.project == "DocumentationProject"
        import uuid as uuidlib
        assert len(result.unit_id) == 36
        uuidlib.UUID(result.unit_id, version=4)
        assert result.role == ChunkRole.DEVELOPER
        
        # Verify the summary
        assert result.summary == "Project introduction section"
        
        # Verify the task and subtask IDs
        assert len(result.task_id) == 36
        uuidlib.UUID(result.task_id, version=4)
        assert len(result.subtask_id) == 36
        uuidlib.UUID(result.subtask_id, version=4)
        
        # Verify source path and lines
        assert result.source_path == "docs/intro.md"
        assert result.source_lines == [1, 3]
        
        # Verify tags
        assert len(result.tags) == 3
        assert "introduction" in result.tags
        assert "documentation" in result.tags
        assert "overview" in result.tags
        
        # Verify links format
        assert len(result.links) == 1
        assert result.links[0].startswith("parent:")
        
        # Verify UUID format
        assert re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            result.uuid,
            re.IGNORECASE
        ) 