"""
Advanced and edge case tests for SemanticChunk.
Tests for complex scenarios, error handling, and advanced functionality.
"""
import pytest
import uuid
from datetime import datetime, timezone
from chunk_metadata_adapter.semantic_chunk import SemanticChunk, ChunkMetrics
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum, ChunkRole, ChunkStatus
import pydantic

def valid_uuid():
    return str(uuid.uuid4())

def test_chunk_role_validation():
    """Test ChunkRole enum validation."""
    chunk = SemanticChunk(
        uuid=valid_uuid(),
        source_id=valid_uuid(),
        body="Test role",
        type=ChunkType.DOC_BLOCK,
        role=ChunkRole.SYSTEM
    )
    assert chunk.role == ChunkRole.SYSTEM

def test_chunk_status_validation():
    """Test ChunkStatus enum validation."""
    chunk = SemanticChunk(
        uuid=valid_uuid(),
        source_id=valid_uuid(),
        body="Test status",
        type=ChunkType.DOC_BLOCK,
        status=ChunkStatus.NEW
    )
    assert chunk.status == ChunkStatus.NEW

def test_chunk_metrics_complex():
    """Test complex ChunkMetrics scenarios."""
    chunk = SemanticChunk(
        uuid=valid_uuid(),
        source_id=valid_uuid(),
        body="Test metrics",
        type=ChunkType.DOC_BLOCK,
        metrics=ChunkMetrics(
            quality_score=0.85,
            coverage=0.9,
            cohesion=0.8,
            used_in_generation=True
        )
    )
    assert chunk.metrics.quality_score == 0.85
    assert chunk.metrics.coverage == 0.9
    assert chunk.metrics.cohesion == 0.8
    assert chunk.metrics.used_in_generation is True

def test_semantic_chunk_with_all_optional_fields():
    """Test SemanticChunk with all optional fields filled."""
    chunk = SemanticChunk(
        uuid=valid_uuid(),
        source_id=valid_uuid(),
        body="Complete chunk with all fields",
        text="Complete chunk with all fields",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.EN,
        summary="A complete test chunk",
        title="Complete Test",
        tags=["test", "complete", "all-fields"],
        links=["parent:some-uuid", "related:another-uuid"],
        role=ChunkRole.SYSTEM,
        status=ChunkStatus.NEW,
        is_public=True,
        ordinal=42,
        year=2024,
        quality_score=0.95,
        source_lines=[1, 100],
        block_meta={"author": "test", "version": "1.0"},
        metrics=ChunkMetrics(quality_score=0.95, used_in_generation=True),
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    assert chunk.uuid is not None
    assert chunk.source_id is not None
    assert chunk.body == "Complete chunk with all fields"
    assert chunk.text == "Complete chunk with all fields"
    assert chunk.type == ChunkType.DOC_BLOCK
    assert chunk.language == LanguageEnum.EN
    assert chunk.summary == "A complete test chunk"
    assert chunk.title == "Complete Test"
    assert chunk.tags == ["test", "complete", "all-fields"]
    assert chunk.links == ["parent:some-uuid", "related:another-uuid"]
    assert chunk.role == ChunkRole.SYSTEM
    assert chunk.status == ChunkStatus.NEW
    assert chunk.is_public is True
    assert chunk.ordinal == 42
    assert chunk.year == 2024
    assert chunk.quality_score == 0.95
    assert chunk.source_lines == [1, 100]
    assert chunk.block_meta == {"author": "test", "version": "1.0"}
    assert chunk.metrics.quality_score == 0.95
    assert chunk.metrics.used_in_generation is True
    assert chunk.created_at is not None

def test_validate_and_fill_comprehensive():
    """Comprehensive test of validate_and_fill with various data types."""
    data = {
        "body": "Test comprehensive validation",
        "type": "DocBlock",
        "language": "en",
        "tags": ["tag1", "tag2"],
        "links": ["parent:uuid1", "related:uuid2"],
        "is_public": "true",
        "quality_score": "0.85",
        "ordinal": "10",
        "year": "2024",
        "source_lines": "[5, 15]",
        "block_meta": '{"key": "value"}',
        "role": "system",
        "status": "new"
    }
    
    chunk, errors = SemanticChunk.validate_and_fill(data)
    assert errors is None
    assert chunk is not None
    assert chunk.body == "Test comprehensive validation"
    assert chunk.type == ChunkType.DOC_BLOCK
    assert chunk.language == LanguageEnum.EN
    assert chunk.tags == ["tag1", "tag2"]
    assert chunk.links == ["parent:uuid1", "related:uuid2"]
    assert chunk.is_public is True
    assert chunk.quality_score == 0.85
    assert chunk.ordinal == 10
    assert chunk.year == 2024
    assert chunk.source_lines == [5, 15]
    assert chunk.block_meta == {"key": "value"}
    assert chunk.role == ChunkRole.SYSTEM
    assert chunk.status == ChunkStatus.NEW

def test_validate_and_fill_error_handling():
    """Test error handling in validate_and_fill."""
    # Test with invalid UUID
    data_bad_uuid = {
        "uuid": "not-a-uuid",
        "body": "Test",
        "type": "DocBlock"
    }
    chunk, errors = SemanticChunk.validate_and_fill(data_bad_uuid)
    assert chunk is None
    assert errors is not None
    assert "uuid" in str(errors).lower()

    # Test with invalid JSON in block_meta
    data_bad_json = {
        "body": "Test",
        "type": "DocBlock",
        "block_meta": "not-valid-json"
    }
    chunk, errors = SemanticChunk.validate_and_fill(data_bad_json)
    assert chunk is None
    assert errors is not None

def test_semantic_chunk_edge_case_values():
    """Test SemanticChunk with edge case values."""
    # Test with minimal valid body
    chunk_minimal = SemanticChunk(
        body="x",  # Minimal valid body (1 character)
        type=ChunkType.DOC_BLOCK
    )
    assert chunk_minimal.body == "x"
    
    # Test with very long text
    long_text = "a" * 10000
    chunk_long = SemanticChunk(
        body=long_text,
        type=ChunkType.DOC_BLOCK
    )
    assert len(chunk_long.body) == 10000
    
    # Test with special characters
    special_text = "Special chars: éñüñ 中文 🚀 \n\t\r"
    chunk_special = SemanticChunk(
        body=special_text,
        type=ChunkType.DOC_BLOCK
    )
    assert chunk_special.body == special_text

def test_semantic_chunk_boundary_values():
    """Test SemanticChunk with boundary values."""
    # Test quality_score boundaries
    chunk_min_quality = SemanticChunk(
        body="Min quality",
        type=ChunkType.DOC_BLOCK,
        quality_score=0.0
    )
    assert chunk_min_quality.quality_score == 0.0
    
    chunk_max_quality = SemanticChunk(
        body="Max quality",
        type=ChunkType.DOC_BLOCK,
        quality_score=1.0
    )
    assert chunk_max_quality.quality_score == 1.0
    
    # Test with zero ordinal
    chunk_zero_ordinal = SemanticChunk(
        body="Zero ordinal",
        type=ChunkType.DOC_BLOCK,
        ordinal=0
    )
    assert chunk_zero_ordinal.ordinal == 0
    
    # Test with very large ordinal
    chunk_large_ordinal = SemanticChunk(
        body="Large ordinal",
        type=ChunkType.DOC_BLOCK,
        ordinal=999999
    )
    assert chunk_large_ordinal.ordinal == 999999

def test_semantic_chunk_invalid_quality_score():
    """Test that invalid quality_score values raise ValidationError."""
    with pytest.raises(pydantic.ValidationError):
        SemanticChunk(
            body="Invalid quality",
            type=ChunkType.DOC_BLOCK,
            quality_score=1.5  # > 1.0
        )
    
    with pytest.raises(pydantic.ValidationError):
        SemanticChunk(
            body="Invalid quality",
            type=ChunkType.DOC_BLOCK,
            quality_score=-0.1  # < 0.0
        )

def test_semantic_chunk_complex_block_meta():
    """Test SemanticChunk with complex block_meta structures."""
    complex_meta = {
        "author": "test_user",
        "version": 1.5,
        "tags": ["meta", "complex"],
        "nested": {
            "level1": {
                "level2": "deep_value"
            }
        },
        "array": [1, 2, 3],
        "boolean": True,
        "null_value": None
    }
    
    chunk = SemanticChunk(
        body="Complex meta test",
        type=ChunkType.DOC_BLOCK,
        block_meta=complex_meta
    )
    
    assert chunk.block_meta == complex_meta
    assert chunk.block_meta["nested"]["level1"]["level2"] == "deep_value"
    assert chunk.block_meta["array"] == [1, 2, 3]
    assert chunk.block_meta["boolean"] is True
    assert chunk.block_meta["null_value"] is None

def test_semantic_chunk_large_tags_and_links():
    """Test SemanticChunk with valid numbers of tags and links."""
    valid_tags = [f"tag_{i}" for i in range(30)]  # Within limit of 32
    valid_links = [f"related:uuid_{i}" for i in range(30)]  # Within limit of 32
    
    chunk = SemanticChunk(
        body="Valid collections test",
        type=ChunkType.DOC_BLOCK,
        tags=valid_tags,
        links=valid_links
    )
    
    assert len(chunk.tags) == 30
    assert len(chunk.links) == 30
    assert chunk.tags[0] == "tag_0"
    assert chunk.tags[29] == "tag_29"
    assert chunk.links[0] == "related:uuid_0"
    assert chunk.links[29] == "related:uuid_29"

def test_semantic_chunk_serialization_complex():
    """Test serialization of complex SemanticChunk instances."""
    complex_chunk = SemanticChunk(
        body="Complex serialization test",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.PYTHON,
        tags=["complex", "serialization", "test"],
        links=["parent:uuid1", "related:uuid2"],
        block_meta={"nested": {"key": "value"}},
        quality_score=0.87,
        ordinal=42,
        year=2024,
        is_public=True,
        role=ChunkRole.SYSTEM,
        status=ChunkStatus.NEW
    )
    
    # Test model_dump
    dict_repr = complex_chunk.model_dump()
    assert isinstance(dict_repr, dict)
    assert dict_repr["body"] == "Complex serialization test"
    assert dict_repr["tags"] == ["complex", "serialization", "test"]
    assert dict_repr["block_meta"] == {"nested": {"key": "value"}}
    
    # Test model_dump_json
    json_repr = complex_chunk.model_dump_json()
    assert isinstance(json_repr, str)
    
    # Test reconstruction
    reconstructed = SemanticChunk.model_validate(dict_repr)
    assert reconstructed.body == complex_chunk.body
    assert reconstructed.tags == complex_chunk.tags
    assert reconstructed.block_meta == complex_chunk.block_meta
    assert reconstructed.quality_score == complex_chunk.quality_score

def test_semantic_chunk_flat_dict_complex():
    """Test flat dict conversion with complex nested structures."""
    chunk = SemanticChunk(
        body="Flat dict complex test",
        type=ChunkType.DOC_BLOCK,
        block_meta={
            "level1": {
                "level2": {
                    "level3": "deep_value"
                },
                "array": [1, 2, 3]
            },
            "simple": "value"
        }
    )
    
    flat_dict = chunk.to_flat_dict()
    assert "block_meta.level1.level2.level3" in flat_dict
    assert flat_dict["block_meta.level1.level2.level3"] == "deep_value"
    assert "block_meta.level1.array" in flat_dict
    assert flat_dict["block_meta.simple"] == "value"
    
    # Test reconstruction
    reconstructed = SemanticChunk.from_flat_dict(flat_dict)
    assert reconstructed.block_meta["level1"]["level2"]["level3"] == "deep_value"
    assert reconstructed.block_meta["simple"] == "value" 