"""
Integration tests for LanguageEnum and SemanticChunk.is_code() method.

Tests the interaction between language detection, chunk types, and code identification
across different components of the system.
"""
import pytest
import uuid
from chunk_metadata_adapter import ChunkMetadataBuilder, SemanticChunk
from chunk_metadata_adapter.data_types import LanguageEnum, ChunkType, ChunkRole, ChunkStatus


class TestLanguageEnumIntegration:
    """Integration tests for LanguageEnum with other system components."""
    
    def test_language_enum_with_chunk_metadata_builder(self):
        """Test LanguageEnum integration with ChunkMetadataBuilder."""
        builder = ChunkMetadataBuilder()
        source_id = str(uuid.uuid4())
        
        # Test building chunks with different programming languages
        test_cases = [
            (LanguageEnum.PYTHON, "def hello():\n    print('Hello, World!')"),
            (LanguageEnum.JAVASCRIPT, "function hello() {\n    console.log('Hello, World!');\n}"),
            (LanguageEnum.JAVA, "public class Hello {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}"),
            (LanguageEnum.ONEC, "Процедура Привет()\n    Сообщить(\"Привет, Мир!\");\nКонецПроцедуры"),
            (LanguageEnum.SQL, "SELECT 'Hello, World!' AS greeting;"),
            (LanguageEnum.HTML, "<html><body><h1>Hello, World!</h1></body></html>"),
            (LanguageEnum.CSS, "body { background-color: #f0f0f0; }"),
            (LanguageEnum.JSON, '{"message": "Hello, World!"}'),
            (LanguageEnum.XML, "<?xml version=\"1.0\"?><greeting>Hello, World!</greeting>"),
            (LanguageEnum.YAML, "greeting: Hello, World!"),
        ]
        
        for language, code_sample in test_cases:
            chunk = builder.build_semantic_chunk(
                body=code_sample,
                language=language,
                chunk_type=ChunkType.CODE_BLOCK,
                source_id=source_id,
                start=0,
                end=len(code_sample)
            )
            
            assert chunk.language == language
            assert chunk.is_code() is True
            assert LanguageEnum.is_programming_language(chunk.language) is True
    
    def test_language_enum_with_natural_languages(self):
        """Test LanguageEnum with natural language content."""
        builder = ChunkMetadataBuilder()
        source_id = str(uuid.uuid4())
        
        test_cases = [
            (LanguageEnum.EN, "This is a sample text in English."),
            (LanguageEnum.RU, "Это пример текста на русском языке."),
            (LanguageEnum.DE, "Das ist ein Beispieltext auf Deutsch."),
            (LanguageEnum.FR, "Ceci est un exemple de texte en français."),
            (LanguageEnum.ES, "Este es un texto de ejemplo en español."),
            (LanguageEnum.ZH, "这是中文示例文本。"),
            (LanguageEnum.JA, "これは日本語のサンプルテキストです。"),
        ]
        
        for language, text_sample in test_cases:
            chunk = builder.build_semantic_chunk(
                body=text_sample,
                language=language,
                chunk_type=ChunkType.DOC_BLOCK,
                source_id=source_id,
                start=0,
                end=len(text_sample)
            )
            
            assert chunk.language == language
            assert chunk.is_code() is False
            assert LanguageEnum.is_programming_language(chunk.language) is False
    
    def test_flat_dict_serialization_with_new_languages(self):
        """Test serialization/deserialization with new programming languages."""
        chunk = SemanticChunk(
            body="Функция ВычислитьСумму(А, Б)\n    Возврат А + Б;\nКонецФункции",
            type=ChunkType.CODE_BLOCK,
            language=LanguageEnum.ONEC,
            role=ChunkRole.DEVELOPER
        )
        
        # Serialize to flat dict
        flat_dict = chunk.to_flat_dict(for_redis=True)
        
        # Check that language is properly serialized
        assert flat_dict["language"] == "1C"
        assert flat_dict["type"] == "CodeBlock"
        
        # Deserialize back
        restored_chunk = SemanticChunk.from_flat_dict(flat_dict)
        
        assert restored_chunk.language == LanguageEnum.ONEC
        assert restored_chunk.type == ChunkType.CODE_BLOCK
        assert restored_chunk.is_code() is True
    
    def test_language_detection_priority(self):
        """Test that CODE_BLOCK type takes priority over language in is_code detection."""
        # CODE_BLOCK with natural language should still be considered code
        chunk = SemanticChunk(
            body="This is documentation written in English but marked as code block.",
            type=ChunkType.CODE_BLOCK,
            language=LanguageEnum.EN
        )
        
        assert chunk.is_code() is True
        assert LanguageEnum.is_programming_language(chunk.language) is False
        
        # DOC_BLOCK with programming language should be considered code
        chunk2 = SemanticChunk(
            body="print('Hello, World!')",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.PYTHON
        )
        
        assert chunk2.is_code() is True
        assert LanguageEnum.is_programming_language(chunk2.language) is True


class TestCodeDetectionScenarios:
    """Test various real-world scenarios for code detection."""
    
    def test_mixed_content_scenarios(self):
        """Test code detection in mixed content scenarios."""
        builder = ChunkMetadataBuilder()
        source_id = str(uuid.uuid4())
        
        # Scenario 1: Documentation with code examples
        doc_with_code = builder.build_semantic_chunk(
            body="Here's how to use the function:\n\n```python\ndef example():\n    return 'Hello'\n```",
            language=LanguageEnum.MARKDOWN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=source_id,
            start=0,
            end=1
        )
        
        # Markdown is considered a programming language in our system
        assert doc_with_code.is_code() is True
        
        # Scenario 2: Configuration files
        config_chunk = builder.build_semantic_chunk(
            body="server:\n  host: localhost\n  port: 8080\ndatabase:\n  url: postgresql://...",
            language=LanguageEnum.YAML,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=source_id,
            start=0,
            end=1
        )
        
        assert config_chunk.is_code() is True
        
        # Scenario 3: SQL queries
        sql_chunk = builder.build_semantic_chunk(
            body="SELECT u.name, COUNT(o.id) as order_count\nFROM users u\nLEFT JOIN orders o ON u.id = o.user_id\nGROUP BY u.id, u.name\nORDER BY order_count DESC;",
            language=LanguageEnum.SQL,
            chunk_type=ChunkType.CODE_BLOCK,
            source_id=source_id,
            start=0,
            end=1
        )
        
        assert sql_chunk.is_code() is True
    
    def test_edge_case_languages(self):
        """Test edge cases with specific programming languages."""
        test_cases = [
            # Assembly code
            (LanguageEnum.ASSEMBLY, "MOV AX, 1\nMOV BX, 2\nADD AX, BX\nINT 21h"),
            
            # Shell script
            (LanguageEnum.SHELL, "#!/bin/bash\necho 'Hello, World!'\nfor i in {1..5}; do\n  echo $i\ndone"),
            
            # PowerShell
            (LanguageEnum.POWERSHELL, "Get-Process | Where-Object {$_.CPU -gt 100} | Sort-Object CPU -Descending"),
            
            # Dockerfile
            (LanguageEnum.DOCKERFILE, "FROM python:3.9-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt"),
            
            # CMake
            (LanguageEnum.CMAKE, "cmake_minimum_required(VERSION 3.10)\nproject(MyProject)\nadd_executable(myapp main.cpp)"),
            
            # INI file
            (LanguageEnum.INI, "[database]\nhost = localhost\nport = 5432\nname = mydb"),
        ]
        
        for language, code_sample in test_cases:
            chunk = SemanticChunk(
                body=code_sample,
                type=ChunkType.DOC_BLOCK,
                language=language
            )
            
            assert chunk.is_code() is True, f"Language {language} should be detected as code"
            assert LanguageEnum.is_programming_language(language) is True, f"Language {language} should be a programming language"
    
    def test_language_case_sensitivity(self):
        """Test that language detection is case-insensitive."""
        test_cases = [
            ("python", LanguageEnum.PYTHON),
            ("PYTHON", LanguageEnum.PYTHON),
            ("Python", LanguageEnum.PYTHON),
            ("javascript", LanguageEnum.JAVASCRIPT),
            ("JavaScript", LanguageEnum.JAVASCRIPT),
            ("JAVASCRIPT", LanguageEnum.JAVASCRIPT),
            ("1c", LanguageEnum.ONEC),
            ("1C", LanguageEnum.ONEC),
        ]
        
        for input_str, expected_enum in test_cases:
            result = LanguageEnum.from_string(input_str)
            assert result == expected_enum, f"Input '{input_str}' should map to {expected_enum}"
            
            # Test eqstr as well
            assert expected_enum.eqstr(input_str) is True, f"'{input_str}' should match {expected_enum}"


def test_comprehensive_guesslang_integration():
    """Test integration with key guesslang-supported languages."""
    # Sample code snippets for different languages
    language_samples = {
        LanguageEnum.C: "#include <stdio.h>\nint main() {\n    printf(\"Hello, World!\\n\");\n    return 0;\n}",
        LanguageEnum.CPP: "#include <iostream>\nint main() {\n    std::cout << \"Hello, World!\" << std::endl;\n    return 0;\n}",
        LanguageEnum.CSHARP: "using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine(\"Hello, World!\");\n    }\n}",
        LanguageEnum.GO: "package main\nimport \"fmt\"\nfunc main() {\n    fmt.Println(\"Hello, World!\")\n}",
        LanguageEnum.RUST: "fn main() {\n    println!(\"Hello, World!\");\n}",
        LanguageEnum.SWIFT: "import Foundation\nprint(\"Hello, World!\")",
        LanguageEnum.KOTLIN: "fun main() {\n    println(\"Hello, World!\")\n}",
        LanguageEnum.SCALA: "object HelloWorld {\n    def main(args: Array[String]): Unit = {\n        println(\"Hello, World!\")\n    }\n}",
        LanguageEnum.HASKELL: "main :: IO ()\nmain = putStrLn \"Hello, World!\"",
        LanguageEnum.ONEC: "Процедура ПриветМир()\n    Сообщить(\"Привет, Мир!\");\nКонецПроцедуры",
    }
    
    builder = ChunkMetadataBuilder()
    source_id = str(uuid.uuid4())
    
    for language, code_sample in language_samples.items():
        chunk = builder.build_semantic_chunk(
            body=code_sample,
            language=language,
            chunk_type=ChunkType.CODE_BLOCK,
            source_id=source_id,
            start=0,
            end=len(code_sample)
        )
        
        assert chunk.language == language, f"Language should be {language}"
        assert chunk.is_code() is True, f"Chunk with language {language} should be detected as code"
        assert LanguageEnum.is_programming_language(language) is True, f"{language} should be a programming language"
        
        # Test round-trip serialization
        flat_dict = chunk.to_flat_dict()
        restored_chunk = SemanticChunk.from_flat_dict(flat_dict)
        
        assert restored_chunk.language == language, f"Restored language should be {language}"
        assert restored_chunk.is_code() is True, f"Restored chunk should still be detected as code"


def test_language_detection_performance():
    """Test that language detection performs well with many lookups."""
    import time
    
    # Test with a reasonable number of lookups
    test_languages = ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "1C"]
    iterations = 100
    
    start_time = time.time()
    for _ in range(iterations):
        for lang_str in test_languages:
            result = LanguageEnum.from_string(lang_str)
            assert result is not None
    end_time = time.time()
    
    # Should complete in reasonable time (less than 1 second for 700 lookups)
    elapsed = end_time - start_time
    assert elapsed < 1.0, f"Language detection took too long: {elapsed:.3f} seconds"


def test_is_code_performance():
    """Test that is_code method performs well."""
    import time
    
    chunks = []
    for i in range(50):
        chunk = SemanticChunk(
            body=f"def function_{i}():\n    return {i}",
            type=ChunkType.CODE_BLOCK if i % 2 == 0 else ChunkType.DOC_BLOCK,
            language=LanguageEnum.PYTHON if i % 3 == 0 else LanguageEnum.EN
        )
        chunks.append(chunk)
    
    iterations = 50
    start_time = time.time()
    for _ in range(iterations):
        for chunk in chunks:
            result = chunk.is_code()
            assert isinstance(result, bool)
    end_time = time.time()
    
    # Should complete in reasonable time (less than 0.5 seconds for 2500 calls)
    elapsed = end_time - start_time
    assert elapsed < 0.5, f"is_code method took too long: {elapsed:.3f} seconds" 