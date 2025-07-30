"""Tests for utility functions."""

import pytest
from bibli.utils import (
    parse_reference,
    normalize_book_name,
    format_reference,
    clean_text,
    extract_keywords,
    validate_translation,
    truncate_text,
    is_valid_url,
)


class TestParseReference:
    """Test reference parsing."""

    def test_single_verse(self):
        """Test parsing single verse reference."""
        result = parse_reference("John 3:16")
        assert result == ("John", 3, 16, 16)

    def test_verse_range(self):
        """Test parsing verse range reference."""
        result = parse_reference("Genesis 1:1-5")
        assert result == ("Genesis", 1, 1, 5)

    def test_chapter_only(self):
        """Test parsing chapter only reference."""
        result = parse_reference("Psalms 23")
        assert result == ("Psalms", 23, None, None)

    def test_multi_word_book(self):
        """Test parsing multi-word book names."""
        result = parse_reference("1 John 3:16")
        assert result == ("1 John", 3, 16, 16)

    def test_invalid_reference(self):
        """Test parsing invalid reference."""
        result = parse_reference("invalid")
        assert result is None


class TestNormalizeBookName:
    """Test book name normalization."""

    def test_common_abbreviations(self):
        """Test common abbreviations."""
        assert normalize_book_name("gen") == "Genesis"
        assert normalize_book_name("john") == "John"
        assert normalize_book_name("1cor") == "1 Corinthians"

    def test_case_insensitive(self):
        """Test case insensitive matching."""
        assert normalize_book_name("GEN") == "Genesis"
        assert normalize_book_name("Gen") == "Genesis"

    def test_full_names(self):
        """Test full book names."""
        assert normalize_book_name("Genesis") == "Genesis"
        assert normalize_book_name("Revelation") == "Revelation"

    def test_unknown_book(self):
        """Test unknown book name."""
        result = normalize_book_name("Unknown")
        assert result == "Unknown"


class TestFormatReference:
    """Test reference formatting."""

    def test_chapter_only(self):
        """Test formatting chapter only."""
        result = format_reference("John", 3)
        assert result == "John 3"

    def test_single_verse(self):
        """Test formatting single verse."""
        result = format_reference("John", 3, 16)
        assert result == "John 3:16"

    def test_verse_range(self):
        """Test formatting verse range."""
        result = format_reference("Genesis", 1, 1, 5)
        assert result == "Genesis 1:1-5"

    def test_same_verse_range(self):
        """Test formatting same verse as range."""
        result = format_reference("John", 3, 16, 16)
        assert result == "John 3:16"


class TestCleanText:
    """Test text cleaning."""

    def test_extra_whitespace(self):
        """Test removing extra whitespace."""
        result = clean_text("  This   has    extra   spaces  ")
        assert result == "This has extra spaces"

    def test_punctuation_spacing(self):
        """Test fixing punctuation spacing."""
        result = clean_text("Hello , world .")
        assert result == "Hello, world."

    def test_empty_text(self):
        """Test empty text."""
        result = clean_text("")
        assert result == ""


class TestExtractKeywords:
    """Test keyword extraction."""

    def test_basic_extraction(self):
        """Test basic keyword extraction."""
        text = "For God so loved the world that he gave his only son"
        keywords = extract_keywords(text)
        assert "god" in keywords  # Function converts to lowercase
        assert "loved" in keywords
        assert "world" in keywords
        assert "the" not in keywords  # Stop word

    def test_minimum_length(self):
        """Test minimum length filtering."""
        text = "I am so happy to be here"
        keywords = extract_keywords(text, min_length=4)
        assert "happy" in keywords
        assert "here" in keywords
        assert "am" not in keywords  # Too short

    def test_max_keywords(self):
        """Test maximum keywords limit."""
        text = "one two three four five six seven eight nine ten eleven twelve"
        keywords = extract_keywords(text, max_keywords=5)
        assert len(keywords) <= 5


class TestValidateTranslation:
    """Test translation validation."""

    def test_valid_translations(self):
        """Test valid translation codes."""
        assert validate_translation("NIV") is True
        assert validate_translation("KJV") is True
        assert validate_translation("ESV") is True

    def test_case_insensitive(self):
        """Test case insensitive validation."""
        assert validate_translation("niv") is True
        assert validate_translation("Niv") is True

    def test_invalid_translation(self):
        """Test invalid translation code."""
        assert validate_translation("INVALID") is False


class TestTruncateText:
    """Test text truncation."""

    def test_no_truncation_needed(self):
        """Test when no truncation is needed."""
        text = "Short text"
        result = truncate_text(text, max_length=20)
        assert result == text

    def test_truncation_with_suffix(self):
        """Test truncation with suffix."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) <= 20
        assert result.endswith("...")

    def test_custom_suffix(self):
        """Test truncation with custom suffix."""
        text = "This is a long text"
        result = truncate_text(text, max_length=10, suffix="[more]")
        assert result.endswith("[more]")


class TestIsValidURL:
    """Test URL validation."""

    def test_valid_urls(self):
        """Test valid URLs."""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://localhost:8000") is True
        assert is_valid_url("https://api.example.com/v1/data") is True

    def test_invalid_urls(self):
        """Test invalid URLs."""
        assert is_valid_url("not-a-url") is False
        assert is_valid_url("ftp://example.com") is False
        assert is_valid_url("") is False
