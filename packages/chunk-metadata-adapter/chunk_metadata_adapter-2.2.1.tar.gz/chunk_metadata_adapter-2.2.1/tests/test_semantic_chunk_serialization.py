"""
Serialization and conversion tests for SemanticChunk.
Tests for flat dict conversion, Redis serialization, and type restoration.
"""
import pytest
import uuid
from datetime import datetime, timezone
from chunk_metadata_adapter.semantic_chunk import SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum
import hashlib
import pydantic

def valid_uuid():
    return str(uuid.uuid4())

def test_flat_dict_conversion_roundtrip():
    """
    Test the roundtrip conversion: semantic -> flat -> semantic
    """
    original_chunk = SemanticChunk(
        uuid=valid_uuid(),
        source_id=valid_uuid(),
        body="testing flat dict roundtrip",
        text="testing flat dict roundtrip",
        type=ChunkType.TASK,
        tags=["a", "b"],
        links=["parent:d1b3e4f5-a1b2-4c3d-8e9f-a0b1c2d3e4f5"],
        block_meta={"author": "tester"},
        quality_score=0.88
    )
    
    flat_dict = original_chunk.to_flat_dict(for_redis=False)
    assert isinstance(flat_dict, dict)
    assert flat_dict['tags'] == ["a", "b"]
    assert flat_dict['links'] == ["parent:d1b3e4f5-a1b2-4c3d-8e9f-a0b1c2d3e4f5"]
    assert flat_dict['block_meta.author'] == 'tester'
    assert flat_dict['quality_score'] == 0.88

    restored_chunk = SemanticChunk.from_flat_dict(flat_dict)
    assert restored_chunk.uuid == original_chunk.uuid
    assert restored_chunk.text == original_chunk.text
    assert restored_chunk.tags == original_chunk.tags
    assert restored_chunk.links == original_chunk.links
    assert restored_chunk.block_meta == original_chunk.block_meta
    assert restored_chunk.quality_score == original_chunk.quality_score

def test_from_flat_dict_with_unknown_fields():
    """
    Test that from_flat_dict correctly handles unknown fields.
    """
    flat_data = {
        "uuid": valid_uuid(),
        "source_id": valid_uuid(),
        "text": "test unknown",
        "type": "Log",
        "body": "b",
        "unknown_field": "some_value",
        "nested.unknown": "another_value"
    }
    chunk = SemanticChunk.from_flat_dict(flat_data)
    assert chunk is not None
    assert chunk.text == "test unknown"
    # Pydantic model should ignore unknown fields
    assert not hasattr(chunk, 'unknown_field')

def test_to_redis_dict_conversion():
    """
    Test the to_redis_dict method and its specific conversions.
    """
    chunk = SemanticChunk(
        uuid=valid_uuid(),
        source_id=valid_uuid(),
        body="testing redis dict",
        text="testing redis dict",
        type=ChunkType.METRIC,
        is_public=True,
        tags=['redis', 'test', '123'], # Now all are strings
        block_meta={'version': 1.0}
    )

    redis_dict = chunk.to_flat_dict(for_redis=True)
    assert redis_dict['is_public'] == 'true'
    assert redis_dict['block_meta.version'] == '1.0'
    assert 'embedding' not in redis_dict
    
    # Check that 'tags' is a list of strings
    assert 'tags' in redis_dict
    assert isinstance(redis_dict['tags'], list)
    assert redis_dict['tags'] == ['redis', 'test', '123']

def test_from_flat_dict_type_restoration():
    """
    Test that from_flat_dict correctly restores types from strings where possible.
    """
    flat = {
        'uuid': valid_uuid(),
        'source_id': valid_uuid(),
        'body': 'body',
        'type': 'Task',
        'is_public': 'true',
        'quality_score': '0.8',
        'ordinal': '50',
        'tags': '["a", "b", "1"]' # JSON string list
    }

    chunk = SemanticChunk.from_flat_dict(flat)
    assert chunk.is_public is True
    assert chunk.quality_score == 0.8
    assert chunk.ordinal == 50
    assert chunk.tags == ["a", "b", "1"]

def test_from_flat_dict_edge_cases():
    """Test from_flat_dict with edge cases for lists and year."""
    # Test empty string and "null" for tags/links
    flat_empty = {
        'uuid': valid_uuid(), 'source_id': valid_uuid(), 'body': 'b', 'type': 'DocBlock',
        'tags': ' ', 'links': 'null'
    }
    chunk_empty = SemanticChunk.from_flat_dict(flat_empty)
    assert chunk_empty.tags == []
    assert chunk_empty.links == []

    # Test year=0 becomes None
    flat_year_zero = {
        'uuid': valid_uuid(), 'source_id': valid_uuid(), 'body': 'b', 'type': 'DocBlock', 'year': 0
    }
    chunk_year_zero = SemanticChunk.from_flat_dict(flat_year_zero)
    assert chunk_year_zero.year is None

    # Test bad list format raises error
    flat_bad_links = {
        'uuid': valid_uuid(), 'source_id': valid_uuid(), 'body': 'b', 'type': 'DocBlock',
        'links': 'not_a_json_list'
    }
    with pytest.raises(ValueError):
        SemanticChunk.from_flat_dict(flat_bad_links)

def test_sha256_validation():
    """Test sha256 validator."""
    with pytest.raises(pydantic.ValidationError):
        SemanticChunk(
            uuid=valid_uuid(), source_id=valid_uuid(), body="body", type=ChunkType.DOC_BLOCK,
            sha256="invalid_hash"
        )
    # Valid hash should pass
    valid_sha = hashlib.sha256(b"text").hexdigest()
    chunk = SemanticChunk(
        uuid=valid_uuid(), source_id=valid_uuid(), body="body", type=ChunkType.DOC_BLOCK,
        sha256=valid_sha
    )
    assert chunk.sha256 == valid_sha

def test_created_at_validation():
    """Test created_at validator."""
    with pytest.raises(pydantic.ValidationError):
        SemanticChunk(
            uuid=valid_uuid(), source_id=valid_uuid(), body="body", type=ChunkType.DOC_BLOCK,
            created_at="not-a-date"
        )
    
    valid_date = datetime.now(timezone.utc).isoformat()
    chunk = SemanticChunk(
        uuid=valid_uuid(), source_id=valid_uuid(), body="body", type=ChunkType.DOC_BLOCK,
        created_at=valid_date
    )
    assert chunk.created_at == valid_date

def test_uuid_validation():
    """Test uuid/chunkid field validators."""
    with pytest.raises(pydantic.ValidationError):
        SemanticChunk(
            uuid="not-a-uuid", source_id=valid_uuid(), body="body", type=ChunkType.DOC_BLOCK
        ) 