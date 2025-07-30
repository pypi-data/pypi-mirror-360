import uuid
import math

import pytest
from chunk_metadata_adapter.data_types import ChunkType, ChunkStatus,BlockType, LanguageEnum
from chunk_metadata_adapter.semantic_chunk import SemanticChunk
from chunk_metadata_adapter.metadata_builder import ChunkMetadataBuilder

from chunk_metadata_adapter import (
    ChunkMetadataBuilder,
    ChunkStatus,
    ChunkType,
    SemanticChunk,
)

TOL = 1e-6


def test_extended_metrics_round_trip():
    """Ensure new metric fields are preserved through conversions."""
    builder = ChunkMetadataBuilder(project="MetricsProject")
    source_id = str(uuid.uuid4())

    # Build semantic chunk with explicit metrics
    semantic_chunk = builder.build_semantic_chunk(
        text="Metrics example",
        body="Metrics example",
        language=LanguageEnum.EN,
        chunk_type="Message",
        source_id=source_id,
        coverage=0.9,
        cohesion=0.8,
        boundary_prev=0.7,
        boundary_next=0.6,
        start=0,
        end=1
    )

    assert math.isclose(semantic_chunk.metrics.coverage, 0.9, abs_tol=TOL)
    assert math.isclose(semantic_chunk.metrics.cohesion, 0.8, abs_tol=TOL)
    assert math.isclose(semantic_chunk.metrics.boundary_prev, 0.7, abs_tol=TOL)
    assert math.isclose(semantic_chunk.metrics.boundary_next, 0.6, abs_tol=TOL)

    # Convert to flat then back
    flat_dict = builder.semantic_to_flat(semantic_chunk)
    restored_chunk = builder.flat_to_semantic(flat_dict)

    assert math.isclose(restored_chunk.metrics.coverage, 0.9, abs_tol=TOL)
    assert math.isclose(restored_chunk.metrics.cohesion, 0.8, abs_tol=TOL)
    assert math.isclose(restored_chunk.metrics.boundary_prev, 0.7, abs_tol=TOL)
    assert math.isclose(restored_chunk.metrics.boundary_next, 0.6, abs_tol=TOL)


def test_status_case_insensitive():
    """Verify that status strings are parsed case-insensitively."""
    builder = ChunkMetadataBuilder()
    chunk_upper = builder.build_semantic_chunk(
        text="Status TEST",
        body="Status TEST",
        language=LanguageEnum.EN,
        chunk_type="Log",
        status="RAW",  # uppercase string
        start=0,
        end=1
    )
    assert chunk_upper.status == ChunkStatus.RAW

    # Direct enum construction should also work
    assert ChunkStatus("CLEANED") == ChunkStatus.CLEANED


def test_metrics_fields_validation():
    builder = ChunkMetadataBuilder(project="TestProj")
    source_id = str(uuid.uuid4())
    # Valid values
    chunk = builder.build_semantic_chunk(
        text="test",
        body="test",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status=ChunkStatus.RELIABLE,
        coverage=0.0,
        cohesion=1.0,
        boundary_prev=0.5,
        boundary_next=1.0,
        start=0,
        end=1
    )
    assert chunk.metrics.coverage == 0.0
    assert chunk.metrics.cohesion == 1.0
    assert chunk.metrics.boundary_prev == 0.5
    assert chunk.metrics.boundary_next == 1.0
    # Invalid values
    with pytest.raises(ValueError):
        builder.build_semantic_chunk(
            text="bad",
            body="bad",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=source_id,
            coverage=-0.1,
            start=0,
            end=1
        )
    with pytest.raises(ValueError):
        builder.build_semantic_chunk(
            text="bad",
            body="bad",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=source_id,
            cohesion=1.1,
            start=0,
            end=1
        )


def test_metrics_round_trip():
    builder = ChunkMetadataBuilder(project="TestProj")
    source_id = str(uuid.uuid4())
    chunk = builder.build_semantic_chunk(
        text="roundtrip",
        body="roundtrip",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        coverage=0.7,
        cohesion=0.6,
        boundary_prev=0.5,
        boundary_next=0.4,
        start=0,
        end=1
    )
    assert chunk.metrics.coverage == 0.7
    assert chunk.metrics.cohesion == 0.6
    assert chunk.metrics.boundary_prev == 0.5
    assert chunk.metrics.boundary_next == 0.4


def test_status_case_insensitivity():
    builder = ChunkMetadataBuilder(project="TestProj")
    source_id = str(uuid.uuid4())
    # Lowercase
    chunk1 = builder.build_semantic_chunk(
        text="status lower",
        body="status lower",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status="reliable",
        start=0,
        end=1
    )
    assert chunk1.status == ChunkStatus.RELIABLE
    # Uppercase
    chunk2 = builder.build_semantic_chunk(
        text="status upper",
        body="status upper",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status="RELIABLE",
        start=0,
        end=1
    )
    assert chunk2.status == ChunkStatus.RELIABLE
    # Mixed case
    chunk3 = builder.build_semantic_chunk(
        text="status mixed",
        body="status mixed",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        status="ReLiAbLe",
        start=0,
        end=1
    )
    assert chunk3.status == ChunkStatus.RELIABLE 