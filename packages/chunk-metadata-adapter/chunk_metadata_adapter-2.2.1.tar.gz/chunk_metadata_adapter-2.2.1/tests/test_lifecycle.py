"""
Tests for data lifecycle functionality.
"""
import uuid
import pytest
from chunk_metadata_adapter import (
    ChunkMetadataBuilder,
    ChunkType, 
    ChunkStatus,
    SemanticChunk
)
from chunk_metadata_adapter.data_types import LanguageEnum


def test_data_lifecycle_statuses():
    """Test that all lifecycle statuses are available and usable."""
    # Verify the lifecycle statuses exist and are in expected order
    assert ChunkStatus.RAW.value == "raw"
    assert ChunkStatus.CLEANED.value == "cleaned"
    assert ChunkStatus.VERIFIED.value == "verified"
    assert ChunkStatus.VALIDATED.value == "validated"
    assert ChunkStatus.RELIABLE.value == "reliable"


def test_create_with_lifecycle_status():
    """Test creating chunks with different lifecycle statuses."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    
    # Test creating chunk with RAW status
    raw_chunk = builder.build_semantic_chunk(
        body="Test raw data",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status=ChunkStatus.RAW,
        start=0,
        end=1
    )
    assert raw_chunk.status == ChunkStatus.RAW
    
    # Test creating chunk with CLEANED status
    cleaned_chunk = builder.build_semantic_chunk(
        body="Test cleaned data",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status=ChunkStatus.CLEANED,
        start=0,
        end=1
    )
    assert cleaned_chunk.status == ChunkStatus.CLEANED
    
    # Test creating chunk with RELIABLE status
    reliable_chunk = builder.build_semantic_chunk(
        body="Test reliable data",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status=ChunkStatus.RELIABLE,
        start=0,
        end=1
    )
    assert reliable_chunk.status == ChunkStatus.RELIABLE


def test_default_status_is_raw():
    """Test that the default status for new chunks is RAW."""
    builder = ChunkMetadataBuilder(project="TestProject")
    chunk = builder.build_semantic_chunk(
        body="Test data",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=str(uuid.uuid4()),
        start=0,
        end=1
        # status not specified, should default to RAW
    )
    assert chunk.status == ChunkStatus.RAW


def test_status_transition():
    """Test transitioning a chunk through the data lifecycle."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    
    # Create initial chunk with RAW status
    chunk = builder.build_semantic_chunk(
        body="User data: John Doe, jdoe@eample.com, New York",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status=ChunkStatus.RAW,
        start=0,
        end=1
    )
    
    # Transition to CLEANED
    chunk.status = ChunkStatus.CLEANED
    chunk.text = "User data: John Doe, jdoe@example.com, New York"  # Fixed typo
    assert chunk.status == ChunkStatus.CLEANED
    
    # Transition to VERIFIED
    chunk.status = ChunkStatus.VERIFIED
    chunk.tags.append("verified_email")
    assert chunk.status == ChunkStatus.VERIFIED
    
    # Transition to VALIDATED
    chunk.status = ChunkStatus.VALIDATED
    chunk.links.append(f"reference:{str(uuid.uuid4())}")
    assert chunk.status == ChunkStatus.VALIDATED
    
    # Transition to RELIABLE
    chunk.status = ChunkStatus.RELIABLE
    chunk.metrics.quality_score = 0.95
    assert chunk.status == ChunkStatus.RELIABLE


def test_filter_chunks_by_status():
    """Test filtering chunks based on their lifecycle status."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    
    # Create chunks with different statuses
    chunks = [
        builder.build_semantic_chunk(
            body=f"Test chunk {i}",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=source_id,
            status=status,
            start=0,
            end=1
        )
        for i, status in enumerate([
            ChunkStatus.RAW,
            ChunkStatus.CLEANED,
            ChunkStatus.VERIFIED,
            ChunkStatus.VALIDATED,
            ChunkStatus.RELIABLE
        ])
    ]
    
    # Define helper function to filter by status
    def filter_by_min_status(chunks_list, min_status):
        status_order = {
            "raw": 1,
            "cleaned": 2,
            "verified": 3,
            "validated": 4,
            "reliable": 5
        }
        min_level = status_order[min_status.value]
        return [
            c for c in chunks_list
            if status_order[c.status] >= min_level
        ]
    
    # Test filtering with different minimum statuses
    assert len(filter_by_min_status(chunks, ChunkStatus.RAW)) == 5
    assert len(filter_by_min_status(chunks, ChunkStatus.CLEANED)) == 4
    assert len(filter_by_min_status(chunks, ChunkStatus.VERIFIED)) == 3
    assert len(filter_by_min_status(chunks, ChunkStatus.VALIDATED)) == 2
    assert len(filter_by_min_status(chunks, ChunkStatus.RELIABLE)) == 1 