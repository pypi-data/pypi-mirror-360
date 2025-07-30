import pytest
from chunk_metadata_adapter.semantic_chunk import SemanticChunk, ChunkMetrics
import uuid
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum
from pydantic import ValidationError

def valid_uuid():
    return str(uuid.uuid4())

def test_get_default_prop_val_error():
    with pytest.raises(ValueError):
        SemanticChunk.get_default_prop_val("not_exist")

def test_source_lines_property_and_setter():
    chunk = SemanticChunk(
        uuid=str(uuid.uuid4()),
        source_id=str(uuid.uuid4()),
        type=ChunkType.DOC_BLOCK,
        body="b",
        text="b",
        language=LanguageEnum.EN,
        start=0,
        end=1
    )
    # По умолчанию None
    assert chunk.source_lines is None
    # Установка
    chunk.source_lines = [10, 20]
    assert chunk.source_lines == [10, 20]
    # Некорректная установка
    chunk.source_lines = [1]
    assert chunk.source_lines is None
    chunk.source_lines = None
    assert chunk.source_lines is None

def test_to_flat_dict_empty_fields():
    data = dict(body="b", type="DocBlock", language="en", start=0, end=1, project="p", task_id=valid_uuid(), subtask_id=valid_uuid(), unit_id=valid_uuid(), chunk_uuid=valid_uuid())
    chunk, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    d = chunk.to_flat_dict(for_redis=False)
    print(f"[test_to_flat_dict_empty_fields] d: {d}")
    assert "tags" in d and d["tags"] == []
    assert "links" in d and d["links"] == []
    assert "link_parent" in d and d["link_parent"] == ""
    assert "link_related" in d and d["link_related"] == ""
    assert "source_lines_start" in d and d["source_lines_start"] == 0
    assert "source_lines_end" in d and d["source_lines_end"] == 0

def test_from_flat_dict_empty_fields():
    d = {"body": "b", "type": "DocBlock", "language": "en", "start": 0, "end": 1, "project": "p", "task_id": valid_uuid(), "subtask_id": valid_uuid(), "unit_id": valid_uuid(), "chunk_uuid": valid_uuid()}
    chunk, err = SemanticChunk.validate_and_fill(d)
    assert err is None
    assert chunk.tags == []
    assert chunk.links == []
    assert chunk.source_lines in (None, [0,0], [1,0])
    from chunk_metadata_adapter.semantic_chunk import ChunkMetrics
    assert chunk.metrics is None or isinstance(chunk.metrics, ChunkMetrics)

def test_validate_metadata_type_error():
    with pytest.raises(ValidationError):
        SemanticChunk(
            uuid=str(uuid.uuid4()),
            source_id=str(uuid.uuid4()),
            type=ChunkType.DOC_BLOCK,
            body="b",
            text="b",
            language=LanguageEnum.EN,
            tags="notalist",
            start=0,
            end=1
        )

def test_fill_text_from_body_autofill():
    values = {"body": "abc", "text": None}
    out = SemanticChunk.fill_text_from_body(values)
    assert out["text"] == "abc"

def test_validate_and_fill_error():
    # Ошибка: невалидный type (validate_and_fill автозаполняет DocBlock)
    data = {"type": "notatype", "body": "b", "language": "en", "start": 0, "end": 1}
    chunk, err = SemanticChunk.validate_and_fill(data)
    assert chunk is not None
    assert chunk.type == "DocBlock"

def test_model_post_init_else():
    # metrics = None, но есть поля для ChunkMetrics
    data = dict(body="b", type="DocBlock", language="en", start=0, end=1, project="p", task_id=str(uuid.uuid4()), subtask_id=str(uuid.uuid4()), unit_id=str(uuid.uuid4()), uuid=str(uuid.uuid4()), quality_score=0.5, used_in_generation=False)
    chunk, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    from chunk_metadata_adapter.semantic_chunk import ChunkMetrics
    assert isinstance(chunk.metrics, ChunkMetrics)
    # source_lines есть, но невалидные
    data = dict(body="b", type="DocBlock", language="en", start=0, end=1, project="p", task_id=str(uuid.uuid4()), subtask_id=str(uuid.uuid4()), unit_id=str(uuid.uuid4()), uuid=str(uuid.uuid4()), source_lines_start=1, used_in_generation=False)
    chunk, err = SemanticChunk.validate_and_fill(data)
    assert err is None

def test_validate_sha256():
    from chunk_metadata_adapter.semantic_chunk import SemanticChunk
    # Валидный
    assert SemanticChunk.validate_sha256("a"*64) == "a"*64
    # Не валидный
    with pytest.raises(ValueError):
        SemanticChunk.validate_sha256("badsha256")

def test_validate_created_at():
    from chunk_metadata_adapter.semantic_chunk import SemanticChunk
    import datetime
    # Валидный
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    assert SemanticChunk.validate_created_at(now) == now
    # Не валидный
    with pytest.raises(ValueError):
        SemanticChunk.validate_created_at("notadate")

def test_validate_embedding():
    from chunk_metadata_adapter.semantic_chunk import SemanticChunk
    # Валидный
    assert SemanticChunk.validate_embedding([1,2,3]) == [1,2,3]
    # Не валидный
    with pytest.raises(ValueError):
        SemanticChunk.validate_embedding(123) 