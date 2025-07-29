import pytest
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole, ChunkStatus, BlockType, LanguageEnum, ComparableEnum

# Test data for all enums
ENUM_TEST_CASES = [
    (ChunkType, "DocBlock", "docblock", "InvalidType"),
    (ChunkRole, "system", "SYSTEM", "InvalidRole"),
    (ChunkStatus, "new", "NEW", "InvalidStatus"),
    (BlockType, "paragraph", "PARAGRAPH", "InvalidBlockType"),
    (LanguageEnum, "en", "EN", "InvalidLang"),
]

@pytest.mark.parametrize("enum_class, valid_str, valid_str_case, invalid_str", ENUM_TEST_CASES)
def test_enum_from_string(enum_class: ComparableEnum, valid_str: str, valid_str_case: str, invalid_str: str):
    """Test the from_string class method for all ComparableEnum subclasses."""
    # Test with a valid string
    result = enum_class.from_string(valid_str)
    assert result is not None
    assert result.value == valid_str or result.value.lower() == valid_str.lower()

    # Test with a case-insensitive valid string
    result_case = enum_class.from_string(valid_str_case)
    assert result_case is not None
    assert result_case == result  # Should be the same enum member

    # Test with an invalid string
    assert enum_class.from_string(invalid_str) is None

    # Test with None
    assert enum_class.from_string(None) is None

    # Test with an empty string
    assert enum_class.from_string("") is None

@pytest.mark.parametrize("enum_class, valid_str, valid_str_case, invalid_str", ENUM_TEST_CASES)
def test_enum_eqstr(enum_class: ComparableEnum, valid_str: str, valid_str_case: str, invalid_str: str):
    """Test the eqstr method for all ComparableEnum subclasses."""
    # Get the first enum member for testing
    first_member = next(iter(enum_class))
    
    # Test with the exact value
    assert first_member.eqstr(first_member.value) is True
    
    # Test with case-insensitive match
    assert first_member.eqstr(first_member.value.upper()) is True
    assert first_member.eqstr(first_member.value.lower()) is True
    
    # Test with invalid string
    assert first_member.eqstr(invalid_str) is False

def test_language_enum_edge_cases():
    """Test edge cases for LanguageEnum."""
    # Check "uk" which was added recently
    assert LanguageEnum.from_string("uk") == LanguageEnum.UK
    assert LanguageEnum.from_string("UA") is None # Should be 'uk'
    assert LanguageEnum.UK.eqstr("uk") is True
    assert LanguageEnum.UK.eqstr("UK") is True

    # Check UNKNOWN
    assert LanguageEnum.from_string("UNKNOWN") == LanguageEnum.UNKNOWN
    assert LanguageEnum.UNKNOWN.eqstr("unknown") is True

def test_language_enum_guesslang_languages():
    """Test that all guesslang programming languages are present."""
    # Test a few key programming languages from guesslang
    programming_languages = [
        "Python", "JavaScript", "Java", "C", "C++", "C#", "Go", "Rust", 
        "TypeScript", "PHP", "Ruby", "Swift", "Kotlin", "Scala", "Haskell",
        "Assembly", "Shell", "SQL", "HTML", "CSS", "JSON", "XML", "YAML"
    ]
    
    for lang in programming_languages:
        enum_value = LanguageEnum.from_string(lang)
        assert enum_value is not None, f"Language {lang} not found in LanguageEnum"
        assert enum_value.value == lang, f"Expected {lang}, got {enum_value.value}"

def test_language_enum_additional_languages():
    """Test additional languages like 1C."""
    # Test 1C language
    onec = LanguageEnum.from_string("1C")
    assert onec == LanguageEnum.ONEC
    assert onec.value == "1C"
    
    # Test case insensitive
    assert LanguageEnum.ONEC.eqstr("1c") is True
    assert LanguageEnum.ONEC.eqstr("1C") is True

def test_language_enum_is_programming_language():
    """Test the is_programming_language class method."""
    # Test natural languages - should return False
    natural_languages = [
        LanguageEnum.UNKNOWN, LanguageEnum.EN, LanguageEnum.RU, 
        LanguageEnum.UK, LanguageEnum.DE, LanguageEnum.FR, 
        LanguageEnum.ES, LanguageEnum.ZH, LanguageEnum.JA
    ]
    
    for lang in natural_languages:
        assert LanguageEnum.is_programming_language(lang) is False, f"{lang} should not be a programming language"
        assert LanguageEnum.is_programming_language(lang.value) is False, f"{lang.value} should not be a programming language"
    
    # Test programming languages - should return True
    programming_languages = [
        LanguageEnum.PYTHON, LanguageEnum.JAVASCRIPT, LanguageEnum.JAVA,
        LanguageEnum.C, LanguageEnum.CPP, LanguageEnum.CSHARP, LanguageEnum.GO,
        LanguageEnum.RUST, LanguageEnum.TYPESCRIPT, LanguageEnum.PHP,
        LanguageEnum.RUBY, LanguageEnum.SWIFT, LanguageEnum.KOTLIN,
        LanguageEnum.SCALA, LanguageEnum.HASKELL, LanguageEnum.ASSEMBLY,
        LanguageEnum.SHELL, LanguageEnum.SQL, LanguageEnum.HTML, LanguageEnum.CSS,
        LanguageEnum.JSON, LanguageEnum.XML, LanguageEnum.YAML, LanguageEnum.ONEC
    ]
    
    for lang in programming_languages:
        assert LanguageEnum.is_programming_language(lang) is True, f"{lang} should be a programming language"
        assert LanguageEnum.is_programming_language(lang.value) is True, f"{lang.value} should be a programming language"
    
    # Test with invalid input
    assert LanguageEnum.is_programming_language("invalid_language") is False
    assert LanguageEnum.is_programming_language(None) is False

def test_language_enum_comprehensive_guesslang_coverage():
    """Test that we have all 54 guesslang languages plus additional ones."""
    # All 54 guesslang languages
    expected_guesslang_languages = {
        "Assembly", "Batchfile", "C", "C#", "C++", "Clojure", "CMake", "COBOL",
        "CoffeeScript", "CSS", "CSV", "Dart", "DM", "Dockerfile", "Elixir",
        "Erlang", "Fortran", "Go", "Groovy", "Haskell", "HTML", "INI", "Java",
        "JavaScript", "JSON", "Julia", "Kotlin", "Lisp", "Lua", "Makefile",
        "Markdown", "Matlab", "Objective-C", "OCaml", "Pascal", "Perl", "PHP",
        "PowerShell", "Prolog", "Python", "R", "Ruby", "Rust", "Scala", "Shell",
        "SQL", "Swift", "TeX", "TOML", "TypeScript", "Verilog", "Visual Basic",
        "XML", "YAML"
    }
    
    # Get all programming language values from enum
    actual_programming_languages = set()
    for lang in LanguageEnum:
        if LanguageEnum.is_programming_language(lang):
            actual_programming_languages.add(lang.value)
    
    # Check that all guesslang languages are present
    missing_languages = expected_guesslang_languages - actual_programming_languages
    assert not missing_languages, f"Missing guesslang languages: {missing_languages}"
    
    # Check that we have additional languages (like 1C)
    additional_languages = actual_programming_languages - expected_guesslang_languages
    assert "1C" in additional_languages, "1C language should be present as additional language"
    
    # Total should be at least 54 + 1 = 55
    assert len(actual_programming_languages) >= 55, f"Expected at least 55 programming languages, got {len(actual_programming_languages)}" 