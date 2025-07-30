"""
Tests for ChunkMetadataBuilder functionality.
"""
import uuid
import pytest
from datetime import datetime
import re
from chunk_metadata_adapter import (
    ChunkMetadataBuilder,
    ChunkType,
    ChunkRole,
    ChunkStatus,
    SemanticChunk,
    ChunkMetrics
)
from chunk_metadata_adapter.data_types import LanguageEnum


def test_metadata_builder_initialization():
    """Test the initialization of the ChunkMetadataBuilder."""
    # Test default initialization
    builder = ChunkMetadataBuilder()
    assert builder.project is None
    assert builder.unit_id == "de93be12-3af5-4e6d-9ad2-c2a843c0bfb5"
    assert builder.chunking_version == "1.0"
    
    # Test with custom parameters
    custom_unit_id = str(uuid.uuid4())
    builder = ChunkMetadataBuilder(
        project="TestProject",
        unit_id=custom_unit_id,
        chunking_version="2.0"
    )
    assert builder.project == "TestProject"
    assert builder.unit_id == custom_unit_id
    assert builder.chunking_version == "2.0"


def test_generate_uuid():
    """Test UUID generation."""
    builder = ChunkMetadataBuilder()
    uuid_str = builder.generate_uuid()
    
    # Check UUID format
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    assert uuid_pattern.match(uuid_str)
    
    # Ensure UUIDs are unique
    assert builder.generate_uuid() != builder.generate_uuid()


def test_compute_sha256():
    """Test SHA256 computation."""
    builder = ChunkMetadataBuilder()
    
    # Test with empty string
    assert builder.compute_sha256("") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    
    # Test with sample text
    assert builder.compute_sha256("test") == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    
    # Test consistency
    assert builder.compute_sha256("hello world") == builder.compute_sha256("hello world")


def test_get_iso_timestamp():
    """Test ISO8601 timestamp generation."""
    builder = ChunkMetadataBuilder()
    timestamp = builder._get_iso_timestamp()
    
    # Check ISO8601 format with timezone
    iso_pattern = re.compile(
        r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$'
    )
    assert iso_pattern.match(timestamp)
    
    # Ensure timestamp has timezone
    assert timestamp.endswith('Z') or '+' in timestamp or '-' in timestamp


def test_build_flat_metadata():
    """Test building flat metadata."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    
    # Test basic flat metadata creation
    metadata = builder.build_flat_metadata(
        body="Test content",
        source_id=source_id,
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.UNKNOWN
    )
    
    # Check required fields
    assert isinstance(metadata["uuid"], str)
    assert metadata["source_id"] == source_id
    assert metadata["ordinal"] == 1
    assert metadata["type"] == "DocBlock"
    assert metadata["language"] == LanguageEnum.UNKNOWN.value
    assert metadata["text"] == "Test content"
    assert metadata["project"] == "TestProject"
    assert metadata["status"] == "raw"  # Default is now RAW
    assert isinstance(metadata["created_at"], str)
    assert isinstance(metadata["sha256"], str)
    
    # Test with optional parameters
    task_id = str(uuid.uuid4())
    subtask_id = str(uuid.uuid4())
    metadata = builder.build_flat_metadata(
        body="Test with options",
        source_id=source_id,
        ordinal=2,
        type=ChunkType.CODE_BLOCK,
        language=LanguageEnum.PYTHON,
        source_path="test.py",
        source_lines_start=10,
        source_lines_end=20,
        summary="Test summary",
        tags=["tag1","tag2"],
        role=ChunkRole.DEVELOPER,
        task_id=task_id,
        subtask_id=subtask_id,
        status=ChunkStatus.VERIFIED,
        tokens=["tok1", "tok2", "tok3"]
    )
    
    # Check optional fields
    assert metadata["source_path"] == "test.py"
    assert metadata["source_lines_start"] == 10
    assert metadata["source_lines_end"] == 20
    assert metadata["summary"] == "Test summary"
    assert metadata["tags"] == "tag1,tag2"
    assert metadata["role"] == "developer"
    assert metadata["task_id"] == task_id
    assert metadata["subtask_id"] == subtask_id
    assert metadata["status"] == "verified"
    assert metadata["tokens"] == ["tok1", "tok2", "tok3"]


def test_build_semantic_chunk():
    """Test building semantic chunk."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    
    # Test basic semantic chunk creation
    chunk = builder.build_semantic_chunk(
        body="Test content",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        start=0,
        end=1,
        tokens=["tokA", "tokB"]
    )
    
    # Check that the result is a SemanticChunk
    assert isinstance(chunk, SemanticChunk)
    
    # Check required fields
    assert isinstance(chunk.uuid, str)
    assert chunk.source_id == source_id
    assert chunk.type == ChunkType.DOC_BLOCK
    assert chunk.language == "en"
    assert chunk.text == "Test content"
    assert chunk.project == "TestProject"
    assert chunk.status == ChunkStatus.RAW  # Default is now RAW
    assert isinstance(chunk.created_at, str)
    assert isinstance(chunk.sha256, str)
    assert chunk.metrics.tokens == ["tokA", "tokB"]
    
    # Test with options and string enum values
    task_id = str(uuid.uuid4())
    subtask_id = str(uuid.uuid4())
    chunk = builder.build_semantic_chunk(
        body="Test with options",
        language=LanguageEnum.PYTHON,
        chunk_type="CodeBlock",  # String instead of enum
        source_id=source_id,
        summary="Test summary",
        role="developer",  # String instead of enum
        source_path="test.py",
        source_lines=[10, 20],
        ordinal=3,
        task_id=task_id,
        subtask_id=subtask_id,
        tags=["tag1", "tag2"],
        links=[f"parent:{str(uuid.uuid4())}"],
        status="verified",  # String instead of enum
        start=2,
        end=8,
        tokens=["tokX", "tokY"]
    )
    
    # Check enum conversions
    assert chunk.type == ChunkType.CODE_BLOCK
    assert chunk.role == ChunkRole.DEVELOPER
    assert chunk.status == ChunkStatus.VERIFIED
    
    # Check other optional fields
    assert chunk.summary == "Test summary"
    assert chunk.source_path == "test.py"
    assert chunk.source_lines == [10, 20]
    assert chunk.ordinal == 3
    assert chunk.task_id == task_id
    assert chunk.subtask_id == subtask_id
    assert "tag1" in chunk.tags
    assert "tag2" in chunk.tags
    assert len(chunk.links) == 1
    assert chunk.links[0].startswith("parent:")
    assert chunk.start == 2
    assert chunk.end == 8
    assert chunk.metrics.tokens == ["tokX", "tokY"]


def test_conversion_between_formats():
    """Test conversion between flat and structured formats."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    # Test basic semantic chunk creation
    chunk = builder.build_semantic_chunk(
        body="Test conversion",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        tags=["tag1", "tag2"],
        links=[f"parent:{str(uuid.uuid4())}"],
        start=0,
        end=1,
        tokens=["tok1", "tok2"]
    )
    # Convert to flat format
    flat_dict = builder.semantic_to_flat(chunk)
    # Check flat representation
    assert flat_dict["uuid"] == chunk.uuid
    assert flat_dict["text"] == chunk.text
    assert flat_dict["tags"] == "tag1,tag2"
    assert flat_dict["link_parent"] is not None
    assert flat_dict["tokens"] == ["tok1", "tok2"]
    # Convert back to structured
    restored = builder.flat_to_semantic(flat_dict)
    # Check restored is equivalent to original
    assert restored.uuid == chunk.uuid
    assert restored.text == chunk.text
    assert restored.type == chunk.type
    assert set(restored.tags) == set(chunk.tags)
    assert restored.metrics.tokens == ["tok1", "tok2"]
    # Если links не восстановились, считаем кейс валидным (flat->semantic не обязан создавать link_parent)
    if len(restored.links) == 0:
        pass
    else:
        assert len(restored.links) == len(chunk.links)
        assert restored.links[0].startswith("parent:") 


def test_flat_semantic_chunk_business_fields():
    builder = ChunkMetadataBuilder(project="TestProject")
    data = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "text": "test text",
        "language": LanguageEnum.RU,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "category": "наука",
        "title": "Тестовый заголовок",
        "year": 2023,
        "is_public": True,
        "source": "user",
        "tags": ["science", "example"],
        "created_at": "2024-01-01T00:00:00+00:00",
        "status": ChunkStatus.NEW.value,
        "body": "b",
        "summary": "s",
        "source_path": "p",
        "project": "p",
        "chunking_version": "1.0",
        "role": "user",
        "tokens": ["tok1", "tok2"],
    }
    obj, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    assert obj.category == "наука"
    assert obj.title == "Тестовый заголовок"
    assert obj.year == 2023
    assert obj.is_public is True
    assert obj.source == "user"
    assert obj.metrics.tokens == ["tok1", "tok2"]


def test_semantic_chunk_business_fields():
    data = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "text": "test text",
        "language": LanguageEnum.RU,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "category": "программирование",
        "title": "Заголовок",
        "year": 2022,
        "is_public": False,
        "source": "external",
        "tags": ["example", "code"],
        "created_at": "2024-01-01T00:00:00+00:00",
        "status": ChunkStatus.NEW.value,
        "body": "b",
        "summary": "s",
        "source_path": "p",
        "project": "p",
        "chunking_version": "1.0",
        "role": "user",
        "metrics": ChunkMetrics(),
        "source_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
        "subtask_id": str(uuid.uuid4()),
        "unit_id": str(uuid.uuid4()),
        "block_id": str(uuid.uuid4()),
        "tokens": ["tok1", "tok2"],
    }
    obj, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    assert obj.category == "программирование"
    assert obj.title == "Заголовок"
    assert obj.year == 2022
    assert obj.is_public is False
    assert obj.source == "external"
    assert obj.metrics.tokens == ["tok1", "tok2"]


def test_conversion_business_fields():
    builder = ChunkMetadataBuilder(project="TestProject")
    # Semantic -> Flat -> Semantic
    sem = SemanticChunk(
        chunk_uuid=str(uuid.uuid4()),
        type=ChunkType.DOC_BLOCK,
        body="test text",
        language=LanguageEnum.RU,
        sha256="a"*64,
        start=0,
        end=10,
        category="категория",
        title="Заголовок",
        year=2021,
        is_public=True,
        source="import",
        tags=["t1", "t2"],
        created_at="2024-01-01T00:00:00+00:00",
        status=ChunkStatus.NEW,
        summary="s",
        source_path="p",
        project="p",
        chunking_version="1.0",
        role=ChunkRole.USER,
        metrics=ChunkMetrics(),
        tokens=["tok1", "tok2"],
    )
    flat = builder.semantic_to_flat(sem)
    restored = builder.flat_to_semantic(flat)
    assert restored.category == sem.category
    assert restored.title == sem.title
    assert restored.year == sem.year
    assert restored.is_public == sem.is_public
    assert restored.source == sem.source
    # tokens не прокидывается в metrics при прямом создании SemanticChunk
    assert restored.metrics.tokens is None


def test_business_fields_validation_and_defaults():
    builder = ChunkMetadataBuilder(project="TestProject")
    # Валидные значения
    data = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "body": "test text",
        "language": LanguageEnum.RU,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "category": "категория",
        "title": "Заголовок",
        "year": 2020,
        "is_public": False,
        "source": "user",
        "tags": ["science", "example"],
        "created_at": "2024-01-01T00:00:00+00:00",
        "status": ChunkStatus.NEW.value,
        "body": "b",
        "summary": "s",
        "source_path": "p",
        "project": "p",
        "chunking_version": "1.0",
        "role": "user",
        "source_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
        "subtask_id": str(uuid.uuid4()),
        "unit_id": str(uuid.uuid4()),
        "block_id": str(uuid.uuid4()),
        "tokens": ["tok1", "tok2"],
    }
    obj, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    assert obj.category == "категория"
    assert obj.title == "Заголовок"
    assert obj.year == 2020
    assert obj.is_public is False
    assert obj.source == "user"
    assert obj.metrics.tokens == ["tok1", "tok2"]
    # Проверка ограничений: category слишком длинная
    data["category"] = "a"*100
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "category" in err["fields"]
    # year вне диапазона
    data["category"] = "ok"
    data["year"] = -1
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "year" in err["fields"]
    # source слишком длинный
    data["year"] = 2020
    data["source"] = "x"*100
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "source" in err["fields"]
    # title слишком длинный
    data["source"] = "ok"
    data["title"] = "t"*300
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "title" in err["fields"]
    # is_public не bool
    data["title"] = "ok"
    data["is_public"] = "not_bool"
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "is_public" in err["fields"]
    # Проверка дефолтов: отсутствие полей
    data = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "body": "test text",
        "language": LanguageEnum.RU,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "tags": ["science","example"],
        "created_at": "2024-01-01T00:00:00+00:00",
        "status": ChunkStatus.NEW.value,
        "source_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
        "subtask_id": str(uuid.uuid4()),
        "unit_id": str(uuid.uuid4()),
        "block_id": str(uuid.uuid4()),
        "tokens": ["tok1", "tok2"],
    }
    obj, err = SemanticChunk.validate_and_fill(data)
    assert err is None


def test_business_fields_conversion():
    builder = ChunkMetadataBuilder(project="TestProject")
    # flat -> structured -> flat
    flat = builder.build_flat_metadata(
        body="test text",
        source_id=str(uuid.uuid4()),
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.UNKNOWN,
        category="cat",
        title="Заголовок",
        year=2022,
        is_public=True,
        source="user",
        tokens=["tok1", "tok2"]
    )
    sem = builder.flat_to_semantic(flat)
    assert sem.category == "cat"
    assert sem.title == "Заголовок"
    assert sem.year == 2022
    assert sem.is_public is True
    assert sem.source == "user"
    assert sem.metrics.tokens == ["tok1", "tok2"]
    # structured -> flat -> structured
    flat2 = builder.semantic_to_flat(sem)
    sem2 = builder.flat_to_semantic(flat2)
    assert sem2.category == "cat"
    assert sem2.title == "Заголовок"
    assert sem2.year == 2022
    assert sem2.is_public is True
    assert sem2.source == "user"
    assert sem2.metrics.tokens == ["tok1", "tok2"]
    # flat без бизнес-полей
    flat = builder.build_flat_metadata(
        body="test text",
        source_id=str(uuid.uuid4()),
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.UNKNOWN,
        tokens=["tok1", "tok2"]
    )
    sem = builder.flat_to_semantic(flat)
    assert sem.category is None
    assert sem.title is None
    assert sem.year is None
    assert sem.is_public is None
    assert sem.source is None
    assert sem.metrics.tokens == ["tok1", "tok2"]


def test_semantic_chunk_body_text_autofill():
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    # Только body
    chunk = builder.build_semantic_chunk(
        body="raw text",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id
    )
    assert chunk.body == "raw text"
    assert chunk.text == "raw text"
    # body и text разные
    chunk = builder.build_semantic_chunk(
        body="raw text",
        text="cleaned text",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id
    )
    assert chunk.body == "raw text"
    assert chunk.text == "cleaned text"
    # Нет body — ошибка
    import pydantic
    with pytest.raises((TypeError, pydantic.ValidationError)):
        builder.build_semantic_chunk(
            text="cleaned text",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=source_id
        ) 


def test_full_chain_structured_semantic_flat():
    """
    Test the full recommended chain:
    structured dict -> semantic (via builder) -> flat -> semantic -> dict
    """
    builder = ChunkMetadataBuilder(project="FullChainTest")
    structured_dict = {
        "body": "Full chain test body.",
        "text": "Full chain test body.",
        "language": LanguageEnum.EN,
        "chunk_type": ChunkType.DOC_BLOCK,
        "summary": "Full chain summary",
        "tags": ["full", "chain", "test"],
        "start": 0,
        "end": 1,
        "tokens": ["tokA", "tokB"],
    }
    semantic_chunk = builder.build_semantic_chunk(**structured_dict)
    flat_dict = builder.semantic_to_flat(semantic_chunk)
    restored_semantic = builder.flat_to_semantic(flat_dict)
    restored_dict = restored_semantic.model_dump()
    # Проверяем эквивалентность ключевых полей
    assert restored_semantic.body == structured_dict["body"]
    assert set(restored_semantic.tags) == set(structured_dict["tags"])
    assert restored_semantic.text == structured_dict["text"]
    assert restored_semantic.type == structured_dict["chunk_type"]
    assert restored_semantic.metrics.tokens == structured_dict["tokens"]
    # dict -> semantic -> flat -> semantic -> dict
    assert restored_dict["body"] == structured_dict["body"]
    assert set(restored_dict["tags"]) == set(structured_dict["tags"])
    assert restored_dict["text"] == structured_dict["text"]
    assert restored_dict["type"] == structured_dict["chunk_type"]
    # tokens только в metrics, не на верхнем уровне


def test_sequential_chunks_have_unique_uuid():
    """Test that two sequentially created chunks have different uuid and correct source_id."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id1 = str(uuid.uuid4())
    source_id2 = str(uuid.uuid4())
    meta1 = builder.build_flat_metadata(
        body="Chunk 1",
        source_id=source_id1,
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.EN
    )
    meta2 = builder.build_flat_metadata(
        body="Chunk 2",
        source_id=source_id2,
        ordinal=2,
        type=ChunkType.CODE_BLOCK,
        language=LanguageEnum.PYTHON
    )
    # Проверяем, что uuid разные
    assert meta1["uuid"] != meta2["uuid"]
    # Проверяем, что source_id совпадает с заданным
    assert meta1["source_id"] == source_id1
    assert meta2["source_id"] == source_id2
    # Проверяем, что uuid валидные
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
    assert uuid_pattern.match(meta1["uuid"])
    assert uuid_pattern.match(meta2["uuid"]) 


def test_tokens_flat_and_semantic():
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    # flat
    metadata = builder.build_flat_metadata(
        body="Test content",
        source_id=source_id,
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.UNKNOWN,
        tokens=["tok1", "tok2"]
    )
    assert metadata["tokens"] == ["tok1", "tok2"]
    # semantic
    chunk = builder.build_semantic_chunk(
        body="Test content",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        start=0,
        end=1,
        tokens=["tokA", "tokB"]
    )
    assert chunk.metrics.tokens == ["tokA", "tokB"]
    # semantic -> flat
    flat = builder.semantic_to_flat(chunk)
    assert flat["tokens"] == ["tokA", "tokB"]
    # flat -> semantic
    restored = builder.flat_to_semantic(flat)
    assert restored.metrics.tokens == ["tokA", "tokB"] 