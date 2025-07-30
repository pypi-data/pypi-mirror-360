"""
Тесты для query_business_examples.py - компактное покрытие.
"""

import pytest
from chunk_metadata_adapter.query_business_examples import (
    example_content_management_queries,
    example_quality_control_queries,
    example_analytics_and_reporting_queries,
    example_search_and_discovery_queries,
    example_maintenance_and_cleanup_queries
)
from chunk_metadata_adapter.chunk_query import ChunkQuery


class TestQueryBusinessExamples:
    """Компактные тесты для query_business_examples.py"""

    def test_example_content_management_queries(self):
        """Тест запросов управления контентом."""
        result = example_content_management_queries()
        assert isinstance(result, list)
        assert len(result) == 4
        for query in result:
            assert isinstance(query, ChunkQuery)

    def test_example_quality_control_queries(self):
        """Тест запросов контроля качества."""
        result = example_quality_control_queries()
        assert isinstance(result, list)
        assert len(result) == 4
        for query in result:
            assert isinstance(query, ChunkQuery)

    def test_example_analytics_and_reporting_queries(self):
        """Тест запросов аналитики."""
        result = example_analytics_and_reporting_queries()
        assert isinstance(result, dict)
        assert 'performance' in result
        assert 'languages' in result
        assert 'engagement' in result
        assert 'lifecycle' in result

    def test_example_search_and_discovery_queries(self):
        """Тест запросов поиска."""
        result = example_search_and_discovery_queries()
        assert isinstance(result, list)
        assert len(result) == 4
        for query in result:
            assert isinstance(query, ChunkQuery)

    def test_example_maintenance_and_cleanup_queries(self):
        """Тест запросов обслуживания."""
        result = example_maintenance_and_cleanup_queries()
        assert isinstance(result, list)
        assert len(result) == 4
        for query in result:
            assert isinstance(query, ChunkQuery)

    def test_all_functions_execute_without_errors(self):
        """Тест, что все функции выполняются без ошибок."""
        functions = [
            example_content_management_queries,
            example_quality_control_queries,
            example_analytics_and_reporting_queries,
            example_search_and_discovery_queries,
            example_maintenance_and_cleanup_queries
        ]
        
        for func in functions:
            result = func()
            assert result is not None 