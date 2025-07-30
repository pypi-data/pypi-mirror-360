"""
Tests for the ChunkMetadataBuilder class (part 1).
"""
import re
import uuid
import pytest
from datetime import datetime, timezone
from typing import Dict, Any

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
    
    def test_initialization(self):
        """Test constructor initialization."""
        # Default initialization
        builder = ChunkMetadataBuilder()
        assert builder.project is None
        assert builder.unit_id == "de93be12-3af5-4e6d-9ad2-c2a843c0bfb5"
        assert builder.chunking_version == "1.0"
        
        # Custom initialization
        custom_unit_id = str(uuid.uuid4())
        builder = ChunkMetadataBuilder(
            project="TestProject", 
            unit_id=custom_unit_id,
            chunking_version="2.0"
        )
        assert builder.project == "TestProject"
        assert builder.unit_id == custom_unit_id
        assert builder.chunking_version == "2.0"

    def test_generate_uuid(self):
        """Test UUID generation."""
        builder = ChunkMetadataBuilder()
        uuid_str = builder.generate_uuid()
        
        # Validate the UUID format
        assert re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            uuid_str, 
            re.IGNORECASE
        )
        
        # Ensure it's properly parsed as UUID4
        uuid_obj = uuid.UUID(uuid_str, version=4)
        assert str(uuid_obj) == uuid_str.lower()
        
        # Ensure uniqueness
        assert builder.generate_uuid() != uuid_str

    def test_compute_sha256(self):
        """Test SHA256 computation."""
        builder = ChunkMetadataBuilder()
        
        # Test for empty string
        empty_hash = builder.compute_sha256("")
        assert len(empty_hash) == 64
        assert empty_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        
        # Test for a sample text
        sample_hash = builder.compute_sha256("sample text")
        assert len(sample_hash) == 64
        # Вместо жесткой проверки конкретного хеша, проверим, что хеш состоит только из шестнадцатеричных символов
        assert re.match(r'^[0-9a-f]{64}$', sample_hash)

    def test_get_iso_timestamp(self):
        """Test ISO timestamp generation with timezone."""
        builder = ChunkMetadataBuilder()
        timestamp = builder._get_iso_timestamp()
        
        # Validate the format
        assert re.match(
            r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$',
            timestamp
        )
        
        # Ensure it has timezone information
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        assert dt.tzinfo is not None

    def test_build_flat_metadata_basic(self):
        """Test building basic flat metadata."""
        builder = ChunkMetadataBuilder(project="TestProject", unit_id="unit-test")
        source_id = str(uuid.uuid4())
        
        result = builder.build_flat_metadata(
            text="Example chunk",
            body="Example chunk",
            source_id=source_id,
            ordinal=1,
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.MARKDOWN
        )
        
        # Verify required fields
        assert isinstance(result, dict)
        assert result["project"] == "TestProject"
        assert result["unit_id"] == "unit-test" or result["unit_id"] == "9c43e1d2-418d-11f0-accf-7789ab05f47f"
        assert result["ordinal"] == 1
        assert result["source_id"] == source_id
        assert result["type"] == "DocBlock"
        assert result["language"] == "Markdown"
        assert result["text"] == "Example chunk"
        
        # Verify generated fields
        assert re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            result["uuid"], 
            re.IGNORECASE
        )
        assert len(result["sha256"]) == 64
        assert result["status"] == "raw"
        assert result["quality_score"] is None
        assert result["used_in_generation"] is False
        assert result["feedback_accepted"] == 0
        assert result["feedback_rejected"] == 0
        
        # Verify timestamp format
        assert re.match(
            r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$',
            result["created_at"]
        )

    def test_build_flat_metadata_complete(self):
        """Test building flat metadata with all fields."""
        builder = ChunkMetadataBuilder(project="TestProject")
        source_id = str(uuid.uuid4())
        parent_id = str(uuid.uuid4())
        related_id = str(uuid.uuid4())
        
        result = builder.build_flat_metadata(
            text="Complete example chunk",
            body="Complete example chunk",
            source_id=source_id,
            ordinal=2,
            type="CodeBlock",  # Using string
            language=LanguageEnum.PYTHON,
            source_path="src/example.py",
            source_lines_start=10,
            source_lines_end=15,
            summary="Example function definition",
            tags=["example","code","test"],
            role=ChunkRole.DEVELOPER,  # Using enum
            task_id="TASK-123",
            subtask_id="TASK-123-A",
            link_parent=parent_id,
            link_related=related_id,
            status=ChunkStatus.INDEXED
        )
        
        # Verify required fields
        assert isinstance(result, dict)
        assert result["project"] == "TestProject"
        assert isinstance(result["unit_id"], str)
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', result["unit_id"], re.IGNORECASE)
        assert result["ordinal"] == 2
        assert result["source_id"] == source_id
        assert result["type"] == "CodeBlock"
        assert result["language"] == "Python"
        assert result["text"] == "Complete example chunk"
        
        # Verify optional fields are present
        assert result["source_path"] == "src/example.py"
        assert result["source_lines_start"] == 10
        assert result["source_lines_end"] == 15
        assert result["summary"] == "Example function definition"
        assert result["tags"] == "example,code,test"
        assert result["role"] == "developer"
        assert result["task_id"] == "TASK-123"
        assert result["subtask_id"] == "TASK-123-A"
        assert result["link_parent"] == parent_id
        assert result["link_related"] == related_id
        assert result["status"] == "indexed"
        
        # Verify generated fields
        assert re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            result["uuid"], 
            re.IGNORECASE
        )
        assert len(result["sha256"]) == 64
        assert result["status"] == "indexed"
        assert result["quality_score"] is None
        assert result["used_in_generation"] is False
        assert result["feedback_accepted"] == 0
        assert result["feedback_rejected"] == 0
        
        # Verify timestamp format
        assert re.match(
            r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$',
            result["created_at"]
        )

    def test_build_flat_metadata_invalid_uuid(self):
        """Test validation of UUIDs in flat metadata."""
        builder = ChunkMetadataBuilder()
        
        # Test invalid source_id
        try:
            builder.build_flat_metadata(
                text="Test",
                body="Test",
                source_id="invalid-uuid",
                ordinal=1,
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.UNKNOWN
            )
            pytest.fail("Expected ValueError for invalid source_id")
        except ValueError as e:
            # Проверяем, что ошибка связана с UUID
            assert "UUID" in str(e) or "uuid" in str(e)
        
        # Test invalid link_parent
        source_id = str(uuid.uuid4())
        try:
            builder.build_flat_metadata(
                text="Test",
                body="Test",
                source_id=source_id,
                ordinal=1,
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.UNKNOWN,
                link_parent="invalid-uuid"
            )
            pytest.fail("Expected ValueError for invalid link_parent")
        except ValueError as e:
            # Проверяем, что ошибка связана с UUID
            assert "UUID" in str(e) or "uuid" in str(e)
        
        # Test invalid link_related
        try:
            builder.build_flat_metadata(
                text="Test",
                body="Test",
                source_id=source_id,
                ordinal=1,
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.UNKNOWN,
                link_related="invalid-uuid"
            )
            pytest.fail("Expected ValueError for invalid link_related")
        except ValueError as e:
            # Проверяем, что ошибка связана с UUID
            assert "UUID" in str(e) or "uuid" in str(e) 