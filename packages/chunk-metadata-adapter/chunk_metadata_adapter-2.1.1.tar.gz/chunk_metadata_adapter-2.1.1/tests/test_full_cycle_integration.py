import uuid
import json
import pytest
from chunk_metadata_adapter import ChunkMetadataBuilder, SemanticChunk, ChunkType, ChunkRole, ChunkStatus, ChunkMetrics
from chunk_metadata_adapter.data_types import LanguageEnum

def test_full_cycle_json_to_flat_and_back():
    builder = ChunkMetadataBuilder(project="IntegrationTest", unit_id="unit-1")
    # 1. Имитация JSON-словаря, как от микросервиса
    source_id = str(uuid.uuid4())
    input_dict = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "body": "raw text",
        "text": "cleaned text",
        "language": LanguageEnum.EN.value,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "project": "IntegrationTest",
        "task_id": str(uuid.uuid4()),
        "subtask_id": str(uuid.uuid4()),
        "unit_id": str(uuid.uuid4()),
        "summary": "sum",
        "source_path": "src.py",
        "created_at": "2024-01-01T00:00:00+00:00",
        "chunking_version": "1.0",
        "links": [f"parent:{str(uuid.uuid4())}"],
        "tags": ["tag1", "tag2"],
        "metrics": {
            "quality_score": 0.9,
            "coverage": 0.8,
            "cohesion": 0.7,
            "boundary_prev": 0.6,
            "boundary_next": 0.5,
            "used_in_generation": True,
            "feedback": {"accepted": 1, "rejected": 0, "modifications": 0}
        },
        "status": ChunkStatus.VALIDATED.value,
        "category": "science",
        "title": "Integration Test",
        "year": 2024,
        "is_public": True,
        "source": "user"
    }
    # 2. Сериализация в JSON и обратно (имитация передачи по сети)
    json_str = json.dumps(input_dict)
    received_dict = json.loads(json_str)
    # 3. Валидация и заполнение фабрикой
    chunk, err = SemanticChunk.validate_and_fill(received_dict)
    assert err is None, f"Validation error: {err}"
    # 4. Преобразование в flat-словарь (для записи в векторную БД)
    flat = builder.semantic_to_flat(chunk)
    # 5. Чтение из flat (имитация чтения из БД)
    restored = builder.flat_to_semantic(flat)
    # 6. Проверка: все обязательные и указанные опциональные поля совпадают
    for key in [
        "type", "body", "text", "language", "sha256", "start", "end", "project", "task_id", "subtask_id", "unit_id", "summary", "source_path", "created_at", "chunking_version", "status", "category", "title", "year", "is_public", "source"
    ]:
        assert getattr(restored, key) == input_dict[key], f"Mismatch in field {key}"
    # Проверка tags и links
    assert set(restored.tags) == set(input_dict["tags"])
    assert set(restored.links) == set(input_dict["links"])
    # Проверка метрик
    for m in ["quality_score", "coverage", "cohesion", "boundary_prev", "boundary_next", "used_in_generation"]:
        assert getattr(restored.metrics, m) == input_dict["metrics"][m]
    assert restored.metrics.feedback.accepted == input_dict["metrics"]["feedback"]["accepted"]
    assert restored.metrics.feedback.rejected == input_dict["metrics"]["feedback"]["rejected"]
    assert restored.metrics.feedback.modifications == input_dict["metrics"]["feedback"]["modifications"]
    # 7. Обратное преобразование в dict (model_dump) и сравнение с исходным (по ключам)
    restored_dict = restored.model_dump()
    for key in input_dict:
        if key in ["metrics", "tags", "links"]:
            continue  # уже проверили выше
        # Если поле могло быть автозаполнено, пропускаем сравнение
        autofill_fields = {"type", "role", "language", "status", "block_type", "chunking_version"}
        if key in autofill_fields:
            continue
        assert restored_dict[key] == input_dict[key], f"Mismatch in dict field {key}"
    # 8. Сериализация обратно в JSON (имитация отдачи наружу)
    out_json = json.dumps(restored_dict, default=str)
    assert isinstance(out_json, str)

def test_full_cycle_tokens():
    builder = ChunkMetadataBuilder(project="IntegrationTest", unit_id="unit-1")
    source_id = str(uuid.uuid4())
    input_dict = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "body": "raw text",
        "text": "cleaned text",
        "language": LanguageEnum.EN.value,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "project": "IntegrationTest",
        "task_id": str(uuid.uuid4()),
        "subtask_id": str(uuid.uuid4()),
        "unit_id": str(uuid.uuid4()),
        "summary": "sum",
        "source_path": "src.py",
        "created_at": "2024-01-01T00:00:00+00:00",
        "chunking_version": "1.0",
        "links": [f"parent:{str(uuid.uuid4())}"],
        "tags": ["tag1", "tag2"],
        "metrics": {
            "quality_score": 0.9,
            "coverage": 0.8,
            "cohesion": 0.7,
            "boundary_prev": 0.6,
            "boundary_next": 0.5,
            "used_in_generation": True,
            "feedback": {"accepted": 1, "rejected": 0, "modifications": 0},
            "tokens": 77
        },
        "status": ChunkStatus.VALIDATED.value,
        "category": "science",
        "title": "Integration Test",
        "year": 2024,
        "is_public": True,
        "source": "user"
    }
    json_str = json.dumps(input_dict)
    received_dict = json.loads(json_str)
    chunk, err = SemanticChunk.validate_and_fill(received_dict)
    assert err is None, f"Validation error: {err}"
    assert chunk.metrics.tokens == 77
    flat = builder.semantic_to_flat(chunk)
    assert flat["tokens"] == 77
    restored = builder.flat_to_semantic(flat)
    assert restored.metrics.tokens == 77
    # Проверка остальных полей
    for key in [
        "uuid", "type", "body", "text", "language", "sha256", "start", "end", "project", "task_id", "subtask_id", "unit_id", "summary", "source_path", "created_at", "chunking_version", "links", "tags", "status", "category", "title", "year", "is_public", "source"
    ]:
        assert getattr(restored, key) == input_dict[key], f"Mismatch in field {key}"
    # Проверка tags и links
    assert set(restored.tags) == set(input_dict["tags"])
    assert set(restored.links) == set(input_dict["links"])
    # Проверка метрик
    for m in ["quality_score", "coverage", "cohesion", "boundary_prev", "boundary_next", "used_in_generation"]:
        assert getattr(restored.metrics, m) == input_dict["metrics"][m]
    assert restored.metrics.feedback.accepted == input_dict["metrics"]["feedback"]["accepted"]
    assert restored.metrics.feedback.rejected == input_dict["metrics"]["feedback"]["rejected"]
    assert restored.metrics.feedback.modifications == input_dict["metrics"]["feedback"]["modifications"]
    # Проверка tokens
    assert restored.metrics.tokens == 77
    # 7. Обратное преобразование в dict (model_dump) и сравнение с исходным (по ключам)
    restored_dict = restored.model_dump()
    for key in input_dict:
        if key in ["metrics", "tags", "links"]:
            continue  # уже проверили выше
        # Если поле могло быть автозаполнено, пропускаем сравнение
        autofill_fields = {"type", "role", "language", "status", "block_type", "chunking_version"}
        if key in autofill_fields:
            continue
        assert restored_dict[key] == input_dict[key], f"Mismatch in dict field {key}"
    # 8. Сериализация обратно в JSON (имитация отдачи наружу)
    out_json = json.dumps(restored_dict, default=str)
    assert isinstance(out_json, str) 