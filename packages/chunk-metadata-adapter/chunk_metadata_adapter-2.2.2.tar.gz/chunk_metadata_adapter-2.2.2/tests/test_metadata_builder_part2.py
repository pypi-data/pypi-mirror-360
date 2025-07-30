"""
Tests for the ChunkMetadataBuilder class (part 2).
"""
import re
import uuid
import pytest
from datetime import datetime, timezone
from typing import Dict, Any
import uuid as uuidlib

from chunk_metadata_adapter import (
    ChunkMetadataBuilder, 
    SemanticChunk, 
    ChunkType, 
    ChunkRole, 
    ChunkStatus
)
from chunk_metadata_adapter.data_types import LanguageEnum


class TestChunkMetadataBuilder:
    """Tests for the ChunkMetadataBuilder class."""
    
    def test_build_semantic_chunk_basic(self):
        """Test building basic semantic chunk."""
        builder = ChunkMetadataBuilder(project="TestProject")
        
        chunk = builder.build_semantic_chunk(
            body="Example semantic chunk",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.MESSAGE,
            start=11,
            end=22
        )
        
        # Verify it's a SemanticChunk instance
        assert isinstance(chunk, SemanticChunk)
        
        # Verify required fields
        assert chunk.text == "Example semantic chunk"
        assert chunk.language == LanguageEnum.EN
        assert chunk.type == ChunkType.MESSAGE
        
        # Verify default values
        assert chunk.project == "TestProject"
        assert chunk.status == ChunkStatus.RAW
        assert len(chunk.unit_id) == 36
        uuidlib.UUID(chunk.unit_id, version=4)
        assert len(chunk.links) == 0
        assert len(chunk.tags) == 0
        
        # Verify generated fields
        assert re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            chunk.uuid, 
            re.IGNORECASE
        )
        assert len(chunk.sha256) == 64
        assert chunk.metrics.quality_score is None
        assert chunk.metrics.used_in_generation is False
        assert chunk.metrics.feedback.accepted == 0
        
        # Verify timestamp format
        assert re.match(
            r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$',
            chunk.created_at
        )
        assert chunk.start == 11
        assert chunk.end == 22

    def test_build_semantic_chunk_complete(self):
        """Test building a complete semantic chunk with all fields."""
        builder = ChunkMetadataBuilder(
            project="CompleteProject", 
            unit_id="test-unit"
        )
        source_id = str(uuid.uuid4())
        parent_id = str(uuid.uuid4())
        
        chunk = builder.build_semantic_chunk(
            body="Complete semantic chunk example",
            language=LanguageEnum.MARKDOWN,
            chunk_type="DocBlock",  # Using string instead of enum
            source_id=source_id,
            summary="Test summary",
            role=ChunkRole.REVIEWER,
            source_path="docs/test.md",
            source_lines=[5, 10],
            ordinal=3,
            task_id="DOCS-123",
            subtask_id="DOCS-123-B",
            links=[f"parent:{parent_id}", f"related:{str(uuid.uuid4())}"],
            tags=["test", "docs", "example"],
            status=ChunkStatus.VERIFIED,
            start=0,
            end=1
        )
        
        # Verify all fields
        assert chunk.text == "Complete semantic chunk example"
        assert chunk.language == LanguageEnum.MARKDOWN
        assert chunk.type == ChunkType.DOC_BLOCK
        assert chunk.source_id == source_id
        assert chunk.summary == "Test summary"
        assert chunk.role == ChunkRole.REVIEWER
        assert chunk.source_path == "docs/test.md"
        assert chunk.source_lines == [5, 10]
        assert chunk.ordinal == 3
        assert len(chunk.task_id) == 36
        uuidlib.UUID(chunk.task_id, version=4)
        assert len(chunk.subtask_id) == 36
        uuidlib.UUID(chunk.subtask_id, version=4)
        assert len(chunk.links) == 2
        assert chunk.links[0].startswith("parent:")
        assert chunk.links[1].startswith("related:")
        assert len(chunk.tags) == 3
        assert "test" in chunk.tags
        assert chunk.status == ChunkStatus.VERIFIED

    def test_build_semantic_chunk_invalid_uuid(self):
        """Test validation of UUIDs in semantic chunk."""
        builder = ChunkMetadataBuilder()
        
        # Test invalid source_id
        try:
            builder.build_semantic_chunk(
                body="Test",
                language=LanguageEnum.EN,
                chunk_type=ChunkType.DOC_BLOCK,
                source_id="invalid-uuid"
            )
            pytest.fail("Expected ValueError for invalid source_id")
        except ValueError as e:
            # Проверяем, что ошибка связана с UUID
            assert "UUID" in str(e) or "uuid" in str(e)
        
        # Test invalid link format
        with pytest.raises(ValueError, match="Link must follow"):
            builder.build_semantic_chunk(
                body="Test",
                language=LanguageEnum.EN,
                chunk_type=ChunkType.DOC_BLOCK,
                links=["invalid-link-format"]
            )
        
        # Test invalid UUID in link
        try:
            builder.build_semantic_chunk(
                body="Test",
                language=LanguageEnum.EN,
                chunk_type=ChunkType.DOC_BLOCK,
                links=[f"parent:invalid-uuid"]
            )
            pytest.fail("Expected ValueError for invalid UUID in link")
        except ValueError as e:
            # Проверяем, что ошибка связана с UUID
            assert "UUID" in str(e) or "uuid" in str(e)

    def test_conversion_between_formats(self):
        """Test conversion between flat and semantic formats."""
        builder = ChunkMetadataBuilder(project="ConversionTest")
        source_id = str(uuid.uuid4())
        
        # Create a semantic chunk
        semantic_chunk = builder.build_semantic_chunk(
            body="Conversion test example",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.COMMENT,
            source_id=source_id,
            summary="Test conversion",
            tags=["test", "conversion"],
            links=[f"parent:{str(uuid.uuid4())}"],
            start=0,
            end=1
        )
        print(f"[test_conversion_between_formats] semantic_chunk.tags: {semantic_chunk.tags}")
        print(f"[test_conversion_between_formats] semantic_chunk.links: {semantic_chunk.links}")
        
        # Convert to flat format
        flat_dict = builder.semantic_to_flat(semantic_chunk)
        print(f"[test_conversion_between_formats] flat_dict.tags: {flat_dict['tags']}")
        print(f"[test_conversion_between_formats] flat_dict.links: {flat_dict['link_parent']}")
        
        # Verify flat format
        assert isinstance(flat_dict, Dict)
        assert flat_dict["uuid"] == semantic_chunk.uuid
        assert flat_dict["text"] == semantic_chunk.text
        assert flat_dict["type"] == "Comment"
        assert flat_dict["tags"] == "test,conversion"
        assert flat_dict["link_parent"] is not None
        
        # Convert back to semantic
        restored_chunk = builder.flat_to_semantic(flat_dict)
        print(f"[test_conversion_between_formats] restored_chunk.tags: {restored_chunk.tags}")
        print(f"[test_conversion_between_formats] restored_chunk.links: {restored_chunk.links}")
        
        # Verify restored semantic chunk
        assert isinstance(restored_chunk, SemanticChunk)
        assert restored_chunk.uuid == semantic_chunk.uuid
        assert restored_chunk.text == semantic_chunk.text
        assert restored_chunk.type == semantic_chunk.type
        assert len(restored_chunk.tags) == 2
        assert "test" in restored_chunk.tags
        print(f"[test_conversion_between_formats] restored_chunk.links: {restored_chunk.links}")
        assert len(restored_chunk.links) == 1
        assert restored_chunk.links[0].startswith("parent:")

    def test_metadata_backward_compatibility(self):
        """Test backward compatibility with build_metadata alias."""
        builder = ChunkMetadataBuilder()
        source_id = str(uuid.uuid4())
        
        # Use the alias
        result1 = builder.build_metadata(
            body="Backward compatibility test",
            source_id=source_id,
            ordinal=1,
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN
        )
        
        # Use the new name
        result2 = builder.build_flat_metadata(
            body="Backward compatibility test",
            source_id=source_id,
            ordinal=1,
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN
        )
        
        # They should be equivalent except for UUID and timestamp
        assert result1["text"] == result2["text"]
        assert result1["source_id"] == result2["source_id"]
        assert result1["type"] == result2["type"]
        assert result1["language"] == result2["language"] 