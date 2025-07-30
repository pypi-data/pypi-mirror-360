import pytest
import json
import uuid
from datetime import datetime, timezone
from chunk_metadata_adapter.semantic_chunk import SemanticChunk, ChunkMetrics, FeedbackMetrics, _autofill_min_length_str_fields
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole, ChunkStatus, LanguageEnum, BlockType
from chunk_metadata_adapter.utils import ChunkId
from pydantic import ValidationError


def test_chunk_metrics_properties():
    """Test ChunkMetrics properties - lines 65-76"""
    feedback = FeedbackMetrics(accepted=5, rejected=2, modifications=3)
    metrics = ChunkMetrics(feedback=feedback)
    
    assert metrics.feedback_accepted == 5
    assert metrics.feedback_rejected == 2
    assert metrics.feedback_modifications == 3


def test_source_lines_property_setter():
    """Test source_lines property setter - lines 169-175"""
    chunk = SemanticChunk(body="test", type=ChunkType.DOC_BLOCK)
    
    # Test setting source_lines
    chunk.source_lines = [10, 20]
    assert chunk.source_lines_start == 10
    assert chunk.source_lines_end == 20
    
    # Test setting to None
    chunk.source_lines = None
    assert chunk.source_lines is None


def test_autofill_min_length_str_fields_function():
    """Test _autofill_min_length_str_fields function - lines 571-583"""
    data = {
        "body": "",  # Empty string, should be filled to min_length
        "summary": ""  # Empty string, should be filled to min_length
    }
    
    # Get model fields for SemanticChunk
    model_fields = SemanticChunk.model_fields
    
    # Apply autofill
    result = _autofill_min_length_str_fields(data, model_fields)
    
    # body has min_length=1, so empty string should be filled
    assert len(result["body"]) >= 1
    # summary has min_length=0, so should remain empty but not None
    assert result["summary"] == ""


def test_validate_and_fill_int_float_handling():
    """Test validate_and_fill with int/float field handling - lines 418-427"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK.value,
        "ordinal": None,  # Should be auto-filled to 0
        "quality_score": None,  # Should be auto-filled based on constraints
        "year": ""  # Empty string should be converted
    }
    chunk, error = SemanticChunk.validate_and_fill(data)
    assert error is None
    assert chunk.ordinal == 0  # Auto-filled to ge constraint
    assert chunk.quality_score == 0.0  # Auto-filled to ge constraint


def test_validate_and_fill_bool_handling():
    """Test validate_and_fill with bool field handling - lines 428-431"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK.value,
        "used_in_generation": None  # Should be auto-filled to False
    }
    chunk, error = SemanticChunk.validate_and_fill(data)
    assert error is None
    assert chunk.used_in_generation is False


def test_validate_and_fill_pydantic_basemodel():
    """Test validate_and_fill with pydantic BaseModel field - lines 436-439"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK.value,
        "metrics": None  # Should be auto-filled to empty ChunkMetrics
    }
    chunk, error = SemanticChunk.validate_and_fill(data)
    assert error is None
    assert isinstance(chunk.metrics, ChunkMetrics)


def test_validate_and_fill_list_handling():
    """Test validate_and_fill with list field handling - lines 440-447"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK.value,
        "tags": None,  # Should be auto-filled to empty list
        "links": None  # Should be auto-filled to empty list
    }
    chunk, error = SemanticChunk.validate_and_fill(data)
    assert error is None
    assert chunk.tags == []
    assert chunk.links == []


def test_validate_and_fill_dict_handling():
    """Test validate_and_fill with dict field handling - lines 448-452"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK.value,
        "block_meta": None  # Should be auto-filled to empty dict
    }
    chunk, error = SemanticChunk.validate_and_fill(data)
    assert error is None
    assert chunk.block_meta == {}


def test_from_flat_dict_year_not_in_data():
    """Test from_flat_dict when year is not in data - lines 218-221"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK.value
        # year not provided
    }
    chunk = SemanticChunk.from_flat_dict(data)
    # year should be None when not provided
    assert chunk.year is None


def test_model_post_init_block_meta_created_at():
    """Test model_post_init removes created_at from block_meta - lines 493-495"""
    chunk = SemanticChunk(
        body="test",
        type=ChunkType.DOC_BLOCK,
        block_meta={"created_at": "2024-01-01", "other": "data"}
    )
    # created_at should be removed from block_meta
    assert "created_at" not in chunk.block_meta
    assert chunk.block_meta["other"] == "data"


def test_model_post_init_source_lines_sync():
    """Test model_post_init syncs source_lines with individual fields - lines 496-499"""
    chunk = SemanticChunk(
        body="test",
        type=ChunkType.DOC_BLOCK,
        source_lines=[5, 15]
    )
    # source_lines should sync to individual fields
    assert chunk.source_lines_start == 5
    assert chunk.source_lines_end == 15


def test_from_flat_dict_empty_tags_null():
    """Test from_flat_dict with empty/null tags - lines 347-352"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK.value,
        "tags": ""  # Empty string
    }
    chunk = SemanticChunk.from_flat_dict(data)
    assert chunk.tags == []


def test_from_flat_dict_empty_links_null():
    """Test from_flat_dict with empty/null links - lines 347-352"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK.value,
        "links": "null"  # String "null"
    }
    chunk = SemanticChunk.from_flat_dict(data)
    assert chunk.links == []


def test_from_flat_dict_empty_embedding_null():
    """Test from_flat_dict with empty/null embedding - lines 347-352"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK.value,
        "embedding": ""  # Empty string
    }
    chunk = SemanticChunk.from_flat_dict(data)
    assert chunk.embedding == [] 