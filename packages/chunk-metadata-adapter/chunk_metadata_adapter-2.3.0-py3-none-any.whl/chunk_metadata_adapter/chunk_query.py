from typing import Optional, Union, Any, List
from pydantic import Field, BaseModel, ConfigDict
from chunk_metadata_adapter.utils import to_flat_dict, from_flat_dict

class ChunkQuery(BaseModel):
    """
    Query/command model for search and delete operations over chunks.
    Позволяет формировать фильтры с операторами сравнения для числовых и вещественных полей.

    Особенности:
    - Все поля, где допустимы только операции равенства (перечисления, идентификаторы, строки, булевы и т.п.), наследуются как Optional.
    - Для полей, где допустимы сравнения (start, end, year, quality_score, coverage, cohesion, boundary_prev, boundary_next), допускается либо исходный тип, либо строка с оператором (например, '>5', '<=10', '[1,5]', 'in:1,2,3').
    - Используется для построения поисковых и delete-команд с гибкой фильтрацией.
    - Все поля опциональны, фильтр может быть полностью пустым.

    Методы:
    - to_flat_dict(for_redis=True): сериализация фильтра в плоский словарь (для Redis или БД)
    - from_flat_dict(data): восстановление фильтра из плоского словаря

    Примеры использования:
    >>> q = ChunkQuery(type='DocBlock', start='>100')
    >>> flat = q.to_flat_dict(for_redis=True)
    >>> q2 = ChunkQuery.from_flat_dict(flat)
    """
    uuid: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Unique identifier (UUIDv4)")
    source_id: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Source identifier (UUIDv4)")
    project: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Project name")
    task_id: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Task identifier (UUIDv4)")
    subtask_id: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Subtask identifier (UUIDv4)")
    unit_id: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Processing unit identifier (UUIDv4)")
    type: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Chunk type (e.g., 'Draft', 'DocBlock')")
    role: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Role in the system")
    language: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Language code (enum)")
    body: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Original chunk text")
    text: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Normalized text for search")
    summary: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Short summary of the chunk")
    ordinal: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Order of the chunk within the source")
    sha256: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="SHA256 hash of the text")
    created_at: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="ISO8601 creation date with timezone")
    status: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Processing status")
    source_path: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Path to the source file")
    quality_score: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Quality score [0,1] (float or comparison string)")
    coverage: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Coverage [0,1] (float or comparison string)")
    cohesion: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Cohesion [0,1] (float or comparison string)")
    boundary_prev: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Boundary similarity with previous chunk (float or comparison string)")
    boundary_next: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Boundary similarity with next chunk (float or comparison string)")
    used_in_generation: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Whether used in generation")
    feedback_accepted: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="How many times the chunk was accepted")
    feedback_rejected: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="How many times the chunk was rejected")
    start: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Start offset (int or comparison string)")
    end: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="End offset (int or comparison string)")
    category: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Business category (e.g., 'science', 'programming', 'news')")
    title: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Title or short name")
    year: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Year (int or comparison string)")
    is_public: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Public visibility (True/False)")
    source: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Data source (e.g., 'user', 'external', 'import')")
    block_type: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Type of the source block (BlockType: 'paragraph', 'message', 'section', 'other')")
    chunking_version: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Version of the chunking algorithm or pipeline")
    metrics: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Full metrics object for compatibility")
    block_id: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="UUIDv4 of the source block")
    embedding: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Embedding vector")
    block_index: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Index of the block in the source document")
    source_lines_start: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Start line in the source file")
    source_lines_end: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="End line in the source file")
    tags: Optional[List[str]] = Field(default=None, description="Categorical tags for the chunk.")
    links: Optional[List[str]] = Field(default=None, description="References to other chunks in the format 'relation:uuid'.")
    block_meta: Optional[dict] = Field(default=None, description="Additional metadata about the block.")
    tags_flat: Optional[str] = Field(default=None, description="Comma-separated tags for flat storage.")
    link_related: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Related chunk UUID")
    link_parent: Optional[Union[str, int, float, bool, dict, list]] = Field(default=None, description="Parent chunk UUID")
    model_config = ConfigDict(extra="allow")

    def to_flat_dict(self, for_redis: bool = True) -> dict:
        """
        Сериализация фильтра в плоский словарь (для Redis или БД).
        Все значения приводятся к строкам, вложенные структуры — к плоским ключам.
        Для фильтра поле created_at не автозаполняется.
        """
        d = to_flat_dict(self.model_dump(), for_redis=for_redis)
        # Для фильтра: created_at не должен автозаполняться
        if 'created_at' in d and self.created_at is None:
            del d['created_at']
        return d

    @classmethod
    def from_flat_dict(cls, data: dict) -> "ChunkQuery":
        """
        Восстановление фильтра из плоского словаря (например, из Redis или БД).
        Не выполняет строгую типизацию, просто заполняет поля по ключам.
        """
        restored = from_flat_dict(data)
        return cls(**restored)

    @classmethod
    def from_dict_with_validation(cls, data: dict) -> ("ChunkQuery", Optional[dict]):
        """
        Factory method: validate input dict and create a filter instance.
        For identifiers and enums: strict validation (UUIDv4, enum values).
        For other fields: allow model type or str (e.g., int or str for start, end, year, etc).
        Returns (instance, errors) — if errors exist, instance is None.
        """
        from pydantic import ValidationError
        import re
        from chunk_metadata_adapter.data_types import (
            ChunkType, ChunkRole, ChunkStatus, BlockType, LanguageEnum
        )
        from chunk_metadata_adapter.utils import ChunkId
        # UUID fields
        uuid_fields = {"uuid", "source_id", "task_id", "subtask_id", "unit_id", "block_id", "link_parent", "link_related"}
        # Enum fields
        enum_fields = {
            "type": ChunkType,
            "role": ChunkRole,
            "status": ChunkStatus,
            "block_type": BlockType,
            "language": LanguageEnum,
        }
        errors = {}
        # 1. Строгая валидация идентификаторов
        for field in uuid_fields:
            if field in data and data[field] is not None:
                val = data[field]
                try:
                    if not isinstance(val, str) or not re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", val, re.IGNORECASE):
                        raise ValueError(f"{field} must be a valid UUIDv4 string")
                except Exception as e:
                    errors.setdefault(field, []).append(str(e))
        # 2. Строгая валидация enum
        for field, enum_cls in enum_fields.items():
            if field in data and data[field] is not None:
                val = data[field]
                try:
                    if not isinstance(val, str) or val not in set(item.value for item in enum_cls):
                        raise ValueError(f"{field} must be one of: {', '.join([item.value for item in enum_cls])}")
                except Exception as e:
                    errors.setdefault(field, []).append(str(e))
        # 3. Остальные поля — допускается тип из модели или str
        # (Pydantic сам обработает, если невалидно)
        # Дополнительная строгая проверка: если поле не uuid/enum и не допускает list/dict, то list/dict не допускается
        allowed_types = (str, int, float, bool, type(None))
        for field, value in data.items():
            if field in uuid_fields or field in enum_fields:
                continue
            if isinstance(value, (list, dict)):
                # Для фильтра допускается list только для tags, links и dict для block_meta
                if field not in ["tags", "links", "block_meta"]:
                    errors.setdefault(field, []).append(f"{field} must be str, int, float, bool or dict (got {type(value).__name__})")
            elif not isinstance(value, allowed_types):
                errors.setdefault(field, []).append(f"{field} must be str/int/float/bool/None, got {type(value).__name__}")
        if errors:
            error_lines = [f"{k}: {', '.join(v)}" for k, v in errors.items()]
            return None, {"error": "; ".join(error_lines), "fields": errors}
        try:
            obj = cls(**data)
            return obj, None
        except ValidationError as e:
            field_errors = {}
            error_lines = []
            for err in e.errors():
                loc = err.get('loc')
                msg = err.get('msg')
                if loc:
                    field = loc[0]
                    field_errors.setdefault(field, []).append(msg)
                    error_lines.append(f"{field}: {msg}")
            return None, {'error': '; '.join(error_lines), 'fields': field_errors}
        except Exception as e:
            return None, {'error': str(e), 'fields': {}}

    def to_json_dict(self) -> dict:
        """
        Возвращает словарь, пригодный для сериализации в JSON и передачи на сервер.
        Все значения приводятся к сериализуемым типам (str, int, float, bool, list, dict, None).
        """
        import json
        def make_json_serializable(obj):
            if isinstance(obj, (str, int, float, bool)) or obj is None:
                return obj
            elif isinstance(obj, list):
                return [make_json_serializable(x) for x in obj]
            elif isinstance(obj, dict):
                return {str(k): make_json_serializable(v) for k, v in obj.items()}
            else:
                return str(obj)
        d = self.model_dump()
        return make_json_serializable(d)

    @classmethod
    def from_json_dict(cls, d: dict) -> "ChunkQuery":
        """
        Восстанавливает экземпляр из словаря, полученного из JSON (например, с сервера).
        """
        return cls(**d) 