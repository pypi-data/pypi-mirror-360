"""
Chunk Metadata Adapter - A package for managing metadata for chunked content.

This package provides tools for creating, managing, and converting metadata 
for chunks of content in various systems, including RAG pipelines, document 
processing, and machine learning training datasets.
"""

from .metadata_builder import ChunkMetadataBuilder
from .semantic_chunk import (
    SemanticChunk,
    ChunkType,
    ChunkRole,
    ChunkStatus,
    ChunkMetrics,
    FeedbackMetrics,
    BlockType,
    LanguageEnum
)
# Если потребуется фильтр — импортировать так:
# from .chunk_query import ChunkQuery

__version__ = "2.2.2"
__all__ = [
    "ChunkMetadataBuilder",
    "ChunkType",
    "ChunkRole",
    "ChunkStatus",
    "SemanticChunk",
    "ChunkMetrics",
    "FeedbackMetrics",
    "BlockType",
    "LanguageEnum",
]
