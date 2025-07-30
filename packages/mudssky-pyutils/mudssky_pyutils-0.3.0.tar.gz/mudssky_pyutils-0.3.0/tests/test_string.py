#!/usr/bin/env python

"""Tests for string module."""

import uuid

from pyutils.string import (
    camel_case,
    capitalize,
    dash_case,
    fuzzy_match,
    gen_all_cases_combination,
    generate_base62_code,
    generate_merge_paths,
    generate_uuid,
    get_file_ext,
    parse_template,
    pascal_case,
    remove_prefix,
    remove_suffix,
    reverse,
    slugify,
    snake_case,
    trim,
    truncate,
    word_count,
)


class TestCamelCase:
    """Test camel_case function."""

    def test_camel_case_basic(self):
        """Test basic camel case conversion."""
        assert camel_case("hello_world") == "helloWorld"
        assert camel_case("test_case_example") == "testCaseExample"

    def test_camel_case_already_camel(self):
        """Test camel case with already camelCase string."""
        assert camel_case("helloWorld") == "helloWorld"

    def test_camel_case_spaces(self):
        """Test camel case with spaces."""
        assert camel_case("hello world") == "helloWorld"

    def test_camel_case_dashes(self):
        """Test camel case with dashes."""
        assert camel_case("hello-world") == "helloWorld"

    def test_camel_case_empty_string(self):
        """Test camel case with empty string."""
        assert camel_case("") == ""

    def test_camel_case_single_word(self):
        """Test camel case with single word."""
        assert camel_case("hello") == "hello"


class TestSnakeCase:
    """Test snake_case function."""

    def test_snake_case_basic(self):
        """Test basic snake case conversion."""
        assert snake_case("helloWorld") == "hello_world"
        assert snake_case("testCaseExample") == "test_case_example"

    def test_snake_case_already_snake(self):
        """Test snake case with already snake_case string."""
        assert snake_case("hello_world") == "hello_world"

    def test_snake_case_spaces(self):
        """Test snake case with spaces."""
        assert snake_case("hello world") == "hello_world"

    def test_snake_case_dashes(self):
        """Test snake case with dashes."""
        assert snake_case("hello-world") == "hello_world"

    def test_snake_case_empty_string(self):
        """Test snake case with empty string."""
        assert snake_case("") == ""

    def test_snake_case_single_word(self):
        """Test snake case with single word."""
        assert snake_case("hello") == "hello"


class TestPascalCase:
    """Test pascal_case function."""

    def test_pascal_case_basic(self):
        """Test basic pascal case conversion."""
        assert pascal_case("hello_world") == "HelloWorld"
        assert pascal_case("test_case_example") == "TestCaseExample"

    def test_pascal_case_camel_case(self):
        """Test pascal case with camelCase input."""
        assert pascal_case("helloWorld") == "HelloWorld"

    def test_pascal_case_spaces(self):
        """Test pascal case with spaces."""
        assert pascal_case("hello world") == "HelloWorld"

    def test_pascal_case_dashes(self):
        """Test pascal case with dashes."""
        assert pascal_case("hello-world") == "HelloWorld"

    def test_pascal_case_empty_string(self):
        """Test pascal case with empty string."""
        assert pascal_case("") == ""

    def test_pascal_case_single_word(self):
        """Test pascal case with single word."""
        assert pascal_case("hello") == "Hello"


class TestDashCase:
    """Test dash_case function."""

    def test_dash_case_basic(self):
        """Test basic dash case conversion."""
        assert dash_case("helloWorld") == "hello-world"
        assert dash_case("testCaseExample") == "test-case-example"

    def test_dash_case_snake_case(self):
        """Test dash case with snake_case input."""
        assert dash_case("hello_world") == "hello-world"

    def test_dash_case_spaces(self):
        """Test dash case with spaces."""
        assert dash_case("hello world") == "hello-world"

    def test_dash_case_already_dash(self):
        """Test dash case with already dash-case string."""
        assert dash_case("hello-world") == "hello-world"

    def test_dash_case_empty_string(self):
        """Test dash case with empty string."""
        assert dash_case("") == ""

    def test_dash_case_single_word(self):
        """Test dash case with single word."""
        assert dash_case("hello") == "hello"


class TestSlugify:
    """Test slugify function."""

    def test_slugify_basic(self):
        """Test basic slugify operation."""
        assert slugify("Hello World!") == "hello-world"
        assert slugify("Test & Example") == "test-example"

    def test_slugify_special_characters(self):
        """Test slugify with special characters."""
        assert slugify("Hello@World#Test!") == "hello-world-test"

    def test_slugify_numbers(self):
        """Test slugify with numbers."""
        assert slugify("Test 123 Example") == "test-123-example"

    def test_slugify_multiple_spaces(self):
        """Test slugify with multiple spaces."""
        assert slugify("Hello    World") == "hello-world"

    def test_slugify_empty_string(self):
        """Test slugify with empty string."""
        assert slugify("") == ""

    def test_slugify_only_special_chars(self):
        """Test slugify with only special characters."""
        assert slugify("!@#$%^&*()") == ""


class TestTruncate:
    """Test truncate function."""

    def test_truncate_basic(self):
        """Test basic truncate operation."""
        assert truncate("Hello World", 5) == "Hello..."

    def test_truncate_no_truncation_needed(self):
        """Test truncate when no truncation needed."""
        assert truncate("Hello", 10) == "Hello"

    def test_truncate_exact_length(self):
        """Test truncate with exact length."""
        assert truncate("Hello", 5) == "Hello"

    def test_truncate_custom_suffix(self):
        """Test truncate with custom suffix."""
        assert truncate("Hello World", 5, ">>") == "Hello>>"

    def test_truncate_empty_string(self):
        """Test truncate with empty string."""
        assert truncate("", 5) == ""

    def test_truncate_zero_length(self):
        """Test truncate with zero length."""
        assert truncate("Hello", 0) == "..."


class TestTrim:
    """Test trim function."""

    def test_trim_basic(self):
        """Test basic trim operation."""
        assert trim("  hello world  ") == "hello world"

    def test_trim_no_whitespace(self):
        """Test trim with no whitespace."""
        assert trim("hello") == "hello"

    def test_trim_only_whitespace(self):
        """Test trim with only whitespace."""
        assert trim("   ") == ""

    def test_trim_empty_string(self):
        """Test trim with empty string."""
        assert trim("") == ""

    def test_trim_tabs_and_newlines(self):
        """Test trim with tabs and newlines."""
        assert trim("\t\nhello\n\t") == "hello"


class TestReverse:
    """Test reverse function."""

    def test_reverse_basic(self):
        """Test basic reverse operation."""
        assert reverse("hello") == "olleh"
        assert reverse("world") == "dlrow"

    def test_reverse_empty_string(self):
        """Test reverse with empty string."""
        assert reverse("") == ""

    def test_reverse_single_char(self):
        """Test reverse with single character."""
        assert reverse("a") == "a"

    def test_reverse_palindrome(self):
        """Test reverse with palindrome."""
        assert reverse("racecar") == "racecar"

    def test_reverse_with_spaces(self):
        """Test reverse with spaces."""
        assert reverse("hello world") == "dlrow olleh"


class TestFuzzyMatch:
    """Test fuzzy_match function."""

    def test_fuzzy_match_exact(self):
        """Test fuzzy match with exact match."""
        assert fuzzy_match("hello", "hello") == 1.0

    def test_fuzzy_match_no_match(self):
        """Test fuzzy match with no match."""
        assert fuzzy_match("hello", "world") == 0.0

    def test_fuzzy_match_partial(self):
        """Test fuzzy match with partial match."""
        score = fuzzy_match("hello", "helo")
        assert 0.0 < score < 1.0

    def test_fuzzy_match_case_insensitive(self):
        """Test fuzzy match case insensitive."""
        assert fuzzy_match("Hello", "hello") == 1.0

    def test_fuzzy_match_empty_strings(self):
        """Test fuzzy match with empty strings."""
        assert fuzzy_match("", "") == 1.0
        assert fuzzy_match("hello", "") == 0.0
        assert fuzzy_match("", "hello") == 0.0


class TestParseTemplate:
    """Test parse_template function."""

    def test_parse_template_basic(self):
        """Test basic template parsing."""
        result = parse_template("Hello {name}!", {"name": "World"})
        assert result == "Hello World!"

    def test_parse_template_multiple_vars(self):
        """Test template parsing with multiple variables."""
        result = parse_template(
            "{greeting} {name}!", {"greeting": "Hello", "name": "World"}
        )
        assert result == "Hello World!"

    def test_parse_template_missing_var(self):
        """Test template parsing with missing variable."""
        result = parse_template("Hello {name}!", {})
        assert result == "Hello {name}!"

    def test_parse_template_no_vars(self):
        """Test template parsing with no variables."""
        result = parse_template("Hello World!", {})
        assert result == "Hello World!"

    def test_parse_template_empty_template(self):
        """Test template parsing with empty template."""
        result = parse_template("", {"name": "World"})
        assert result == ""


class TestGenerateUuid:
    """Test generate_uuid function."""

    def test_generate_uuid_format(self):
        """Test that generated UUID has correct format."""
        result = generate_uuid()
        # Check if it's a valid UUID format
        try:
            uuid.UUID(result)
            assert True
        except ValueError:
            raise AssertionError(f"Generated UUID {result} is not valid") from None

    def test_generate_uuid_uniqueness(self):
        """Test that generated UUIDs are unique."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2

    def test_generate_uuid_length(self):
        """Test that generated UUID has correct length."""
        result = generate_uuid()
        assert len(result) == 36  # Standard UUID length with hyphens


class TestGenerateBase62Code:
    """Test generate_base62_code function."""

    def test_generate_base62_code_default_length(self):
        """Test base62 code generation with default length."""
        result = generate_base62_code()
        assert len(result) == 8  # Default length
        assert all(c.isalnum() for c in result)

    def test_generate_base62_code_custom_length(self):
        """Test base62 code generation with custom length."""
        result = generate_base62_code(12)
        assert len(result) == 12
        assert all(c.isalnum() for c in result)

    def test_generate_base62_code_uniqueness(self):
        """Test that generated codes are unique."""
        code1 = generate_base62_code()
        code2 = generate_base62_code()
        assert code1 != code2

    def test_generate_base62_code_zero_length(self):
        """Test base62 code generation with zero length."""
        result = generate_base62_code(0)
        assert result == ""


class TestGetFileExt:
    """Test get_file_ext function."""

    def test_get_file_ext_basic(self):
        """Test basic file extension extraction."""
        assert get_file_ext("file.txt") == "txt"
        assert get_file_ext("image.png") == "png"

    def test_get_file_ext_multiple_dots(self):
        """Test file extension with multiple dots."""
        assert get_file_ext("file.tar.gz") == "gz"

    def test_get_file_ext_no_extension(self):
        """Test file with no extension."""
        assert get_file_ext("filename") == ""

    def test_get_file_ext_hidden_file(self):
        """Test hidden file with extension."""
        assert get_file_ext(".gitignore") == ""
        assert get_file_ext(".config.json") == "json"

    def test_get_file_ext_path(self):
        """Test file extension from path."""
        assert get_file_ext("/path/to/file.txt") == "txt"
        assert get_file_ext("C:\\path\\to\\file.exe") == "exe"

    def test_get_file_ext_empty_string(self):
        """Test file extension with empty string."""
        assert get_file_ext("") == ""


class TestGenerateMergePaths:
    """Test generate_merge_paths function."""

    def test_generate_merge_paths_basic(self):
        """Test basic path merging."""
        result = generate_merge_paths(["path1", "path2", "file.txt"])
        expected = "path1/path2/file.txt"
        assert result == expected

    def test_generate_merge_paths_single_path(self):
        """Test path merging with single path."""
        result = generate_merge_paths(["file.txt"])
        assert result == "file.txt"

    def test_generate_merge_paths_empty_list(self):
        """Test path merging with empty list."""
        result = generate_merge_paths([])
        assert result == ""

    def test_generate_merge_paths_with_slashes(self):
        """Test path merging with existing slashes."""
        result = generate_merge_paths(["path1/", "/path2/", "file.txt"])
        expected = "path1/path2/file.txt"
        assert result == expected

    def test_generate_merge_paths_empty_segments(self):
        """Test path merging with empty segments."""
        result = generate_merge_paths(["path1", "", "path2", "file.txt"])
        expected = "path1/path2/file.txt"
        assert result == expected


class TestWordCount:
    """Test word_count function."""

    def test_word_count_basic(self):
        """Test basic word counting."""
        assert word_count("hello world") == 2
        assert word_count("one two three four") == 4

    def test_word_count_single_word(self):
        """Test word count with single word."""
        assert word_count("hello") == 1

    def test_word_count_empty_string(self):
        """Test word count with empty string."""
        assert word_count("") == 0

    def test_word_count_only_whitespace(self):
        """Test word count with only whitespace."""
        assert word_count("   ") == 0

    def test_word_count_multiple_spaces(self):
        """Test word count with multiple spaces."""
        assert word_count("hello    world") == 2

    def test_word_count_punctuation(self):
        """Test word count with punctuation."""
        assert word_count("hello, world!") == 2


class TestCapitalize:
    """Test capitalize function."""

    def test_capitalize_basic(self):
        """Test basic capitalization."""
        assert capitalize("hello world") == "Hello World"
        assert capitalize("test case example") == "Test Case Example"

    def test_capitalize_already_capitalized(self):
        """Test capitalize with already capitalized string."""
        assert capitalize("Hello World") == "Hello World"

    def test_capitalize_mixed_case(self):
        """Test capitalize with mixed case."""
        assert capitalize("hELLo WoRLd") == "Hello World"

    def test_capitalize_single_word(self):
        """Test capitalize with single word."""
        assert capitalize("hello") == "Hello"

    def test_capitalize_empty_string(self):
        """Test capitalize with empty string."""
        assert capitalize("") == ""

    def test_capitalize_only_spaces(self):
        """Test capitalize with only spaces."""
        assert capitalize("   ") == "   "


class TestRemovePrefix:
    """Test remove_prefix function."""

    def test_remove_prefix_basic(self):
        """Test basic prefix removal."""
        assert remove_prefix("hello world", "hello ") == "world"
        assert remove_prefix("test_file.txt", "test_") == "file.txt"

    def test_remove_prefix_no_match(self):
        """Test prefix removal with no match."""
        assert remove_prefix("hello world", "hi ") == "hello world"

    def test_remove_prefix_empty_prefix(self):
        """Test prefix removal with empty prefix."""
        assert remove_prefix("hello world", "") == "hello world"

    def test_remove_prefix_empty_string(self):
        """Test prefix removal with empty string."""
        assert remove_prefix("", "hello") == ""

    def test_remove_prefix_exact_match(self):
        """Test prefix removal with exact match."""
        assert remove_prefix("hello", "hello") == ""


class TestRemoveSuffix:
    """Test remove_suffix function."""

    def test_remove_suffix_basic(self):
        """Test basic suffix removal."""
        assert remove_suffix("hello world", " world") == "hello"
        assert remove_suffix("file.txt", ".txt") == "file"

    def test_remove_suffix_no_match(self):
        """Test suffix removal with no match."""
        assert remove_suffix("hello world", " universe") == "hello world"

    def test_remove_suffix_empty_suffix(self):
        """Test suffix removal with empty suffix."""
        assert remove_suffix("hello world", "") == "hello world"

    def test_remove_suffix_empty_string(self):
        """Test suffix removal with empty string."""
        assert remove_suffix("", "world") == ""

    def test_remove_suffix_exact_match(self):
        """Test suffix removal with exact match."""
        assert remove_suffix("hello", "hello") == ""


class TestGenAllCasesCombination:
    """Test gen_all_cases_combination function."""

    def test_gen_all_cases_combination_basic(self):
        """Test basic case combination generation."""
        result = gen_all_cases_combination("hello_world")
        expected_cases = {
            "camelCase": "helloWorld",
            "snake_case": "hello_world",
            "PascalCase": "HelloWorld",
            "dash-case": "hello-world",
        }
        assert result == expected_cases

    def test_gen_all_cases_combination_single_word(self):
        """Test case combination with single word."""
        result = gen_all_cases_combination("hello")
        expected_cases = {
            "camelCase": "hello",
            "snake_case": "hello",
            "PascalCase": "Hello",
            "dash-case": "hello",
        }
        assert result == expected_cases

    def test_gen_all_cases_combination_empty_string(self):
        """Test case combination with empty string."""
        result = gen_all_cases_combination("")
        expected_cases = {
            "camelCase": "",
            "snake_case": "",
            "PascalCase": "",
            "dash-case": "",
        }
        assert result == expected_cases

    def test_gen_all_cases_combination_complex(self):
        """Test case combination with complex string."""
        result = gen_all_cases_combination("test_case_example")
        expected_cases = {
            "camelCase": "testCaseExample",
            "snake_case": "test_case_example",
            "PascalCase": "TestCaseExample",
            "dash-case": "test-case-example",
        }
        assert result == expected_cases
