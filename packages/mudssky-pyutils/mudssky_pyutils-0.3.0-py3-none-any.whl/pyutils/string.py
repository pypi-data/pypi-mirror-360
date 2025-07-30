"""String utility functions.

This module provides utility functions for working with strings,
ported from the jsutils library.
"""

import re
import string as string_module
import uuid


def gen_all_cases_combination(text: str) -> dict[str, str]:
    """Generate all common case combinations of a string.

    Args:
        text: Input string

    Returns:
        Dictionary with different case styles

    Examples:
        >>> result = gen_all_cases_combination('hello_world')
        >>> result['camelCase']
        'helloWorld'
        >>> result['PascalCase']
        'HelloWorld'
    """
    return {
        "camelCase": camel_case(text),
        "snake_case": snake_case(text),
        "PascalCase": pascal_case(text),
        "dash-case": dash_case(text),
    }


def generate_uuid() -> str:
    """Generate a UUID string.

    Returns:
        UUID string

    Examples:
        >>> uuid_str = generate_uuid()
        >>> len(uuid_str)
        36
        >>> '-' in uuid_str
        True
    """
    return str(uuid.uuid4())


def generate_base62_code(length: int = 8) -> str:
    """Generate a random Base62 string.

    Args:
        length: Length of the generated string, defaults to 8

    Returns:
        Random Base62 string

    Examples:
        >>> code = generate_base62_code(10)
        >>> len(code)
        10
        >>> all(c in string_module.ascii_letters + string_module.digits for c in code)
        True
    """
    import secrets

    chars = string_module.ascii_letters + string_module.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def fuzzy_match(pattern: str, text: str) -> float:
    """Calculate fuzzy match score between pattern and text.

    Args:
        pattern: Pattern to match
        text: Text to search in

    Returns:
        Similarity score between 0.0 and 1.0

    Examples:
        >>> fuzzy_match('hello', 'hello')
        1.0
        >>> fuzzy_match('hello', 'world')
        0.0
        >>> fuzzy_match('hello', 'helo')
        0.8
    """
    if not pattern and not text:
        return 1.0
    if not pattern or not text:
        return 0.0

    pattern = pattern.lower()
    text = text.lower()

    if pattern == text:
        return 1.0

    # Simple character-based similarity
    matches = 0
    pattern_idx = 0

    for char in text:
        if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
            matches += 1
            pattern_idx += 1

    # Calculate similarity based on matched characters vs pattern length
    return matches / len(pattern) if len(pattern) > 0 else 0.0


def get_file_ext(filename: str) -> str:
    """Get file extension from filename.

    Args:
        filename: Filename to extract extension from

    Returns:
        File extension (without dot)

    Examples:
        >>> get_file_ext('document.pdf')
        'pdf'
        >>> get_file_ext('archive.tar.gz')
        'gz'
        >>> get_file_ext('README')
        ''
        >>> get_file_ext('.gitignore')
        ''
        >>> get_file_ext('.config.json')
        'json'
    """
    if not filename or "." not in filename:
        return ""

    # Extract just the filename from path
    basename = filename.split("/")[-1].split("\\")[-1]

    # Handle hidden files (starting with .)
    if basename.startswith("."):
        # Count dots to determine if there's an extension
        dot_count = basename.count(".")
        if dot_count == 1:  # Only one dot at the beginning, no extension
            return ""
        else:  # Multiple dots, last part is extension
            return basename.split(".")[-1]

    # Regular files
    return basename.split(".")[-1]


def capitalize(text: str) -> str:
    """Capitalize the first letter of each word in a string.

    Args:
        text: Input string

    Returns:
        String with first letter of each word capitalized

    Examples:
        >>> capitalize('hello world')
        'Hello World'
        >>> capitalize('HELLO')
        'Hello'
        >>> capitalize('   ')
        '   '
    """
    if not text:
        return text
    if not text.strip():
        return text
    return " ".join(word.capitalize() for word in text.split())


def camel_case(text: str) -> str:
    """Convert string to camelCase.

    Args:
        text: Input string

    Returns:
        camelCase string

    Examples:
        >>> camel_case('hello world')
        'helloWorld'
        >>> camel_case('hello-world-test')
        'helloWorldTest'
        >>> camel_case('hello_world_test')
        'helloWorldTest'
        >>> camel_case('helloWorld')
        'helloWorld'
    """
    if not text:
        return ""

    # First, split on camelCase boundaries
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    # Then split on spaces, hyphens, underscores
    words = re.split(r"[\s\-_]+", text.strip())
    words = [word for word in words if word]

    if not words:
        return ""

    # First word lowercase, rest title case
    result = words[0].lower()
    for word in words[1:]:
        result += word.capitalize()

    return result


def snake_case(text: str) -> str:
    """Convert string to snake_case.

    Args:
        text: Input string

    Returns:
        snake_case string

    Examples:
        >>> snake_case('Hello World')
        'hello_world'
        >>> snake_case('helloWorld')
        'hello_world'
        >>> snake_case('hello-world')
        'hello_world'
    """
    # Insert underscore before uppercase letters that follow lowercase letters
    text = re.sub(r"([a-z])([A-Z])", r"\1_\2", text)
    # Replace spaces and hyphens with underscores
    text = re.sub(r"[\s\-]+", "_", text)
    # Convert to lowercase
    return text.lower()


def dash_case(text: str) -> str:
    """Convert string to dash-case (kebab-case).

    Args:
        text: Input string

    Returns:
        dash-case string

    Examples:
        >>> dash_case('Hello World')
        'hello-world'
        >>> dash_case('helloWorld')
        'hello-world'
        >>> dash_case('hello_world')
        'hello-world'
    """
    # Insert hyphen before uppercase letters that follow lowercase letters
    text = re.sub(r"([a-z])([A-Z])", r"\1-\2", text)
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Convert to lowercase
    return text.lower()


def pascal_case(text: str) -> str:
    """Convert string to PascalCase.

    Args:
        text: Input string

    Returns:
        PascalCase string

    Examples:
        >>> pascal_case('hello world')
        'HelloWorld'
        >>> pascal_case('hello-world-test')
        'HelloWorldTest'
        >>> pascal_case('hello_world_test')
        'HelloWorldTest'
        >>> pascal_case('helloWorld')
        'HelloWorld'
    """
    if not text:
        return ""

    # First, split on camelCase boundaries
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    # Then split on spaces, hyphens, underscores
    words = re.split(r"[\s\-_]+", text.strip())
    words = [word for word in words if word]

    if not words:
        return ""

    # Capitalize each word
    return "".join(word.capitalize() for word in words)


def parse_template(template: str, variables: dict[str, str | int | float]) -> str:
    """Parse template string with variable substitution.

    Args:
        template: Template string with {variable} placeholders
        variables: Dictionary of variable values

    Returns:
        Parsed string with variables substituted

    Examples:
        >>> parse_template('Hello {name}!', {'name': 'World'})
        'Hello World!'
        >>> parse_template('{greeting} {name}, you are {age} years old',
        ...                {'greeting': 'Hi', 'name': 'Alice', 'age': 25})
        'Hi Alice, you are 25 years old'
    """
    result = template
    for key, value in variables.items():
        placeholder = "{" + key + "}"
        result = result.replace(placeholder, str(value))
    return result


def trim(text: str, chars: str | None = None) -> str:
    """Remove specified characters from both ends of string.

    Args:
        text: Input string
        chars: Characters to remove, defaults to whitespace

    Returns:
        Trimmed string

    Examples:
        >>> trim('  hello  ')
        'hello'
        >>> trim('...hello...', '.')
        'hello'
        >>> trim('abcHELLOcba', 'abc')
        'HELLO'
    """
    if chars is None:
        return text.strip()
    return text.strip(chars)


def trim_start(text: str, chars: str | None = None) -> str:
    """Remove specified characters from the start of string.

    Args:
        text: Input string
        chars: Characters to remove, defaults to whitespace

    Returns:
        Left-trimmed string

    Examples:
        >>> trim_start('  hello  ')
        'hello  '
        >>> trim_start('...hello...', '.')
        'hello...'
    """
    if chars is None:
        return text.lstrip()
    return text.lstrip(chars)


def trim_end(text: str, chars: str | None = None) -> str:
    """Remove specified characters from the end of string.

    Args:
        text: Input string
        chars: Characters to remove, defaults to whitespace

    Returns:
        Right-trimmed string

    Examples:
        >>> trim_end('  hello  ')
        '  hello'
        >>> trim_end('...hello...', '.')
        '...hello'
    """
    if chars is None:
        return text.rstrip()
    return text.rstrip(chars)


def remove_prefix(text: str, prefix: str) -> str:
    """Remove prefix from string if present.

    Args:
        text: Input string
        prefix: Prefix to remove

    Returns:
        String with prefix removed

    Examples:
        >>> remove_prefix('hello world', 'hello ')
        'world'
        >>> remove_prefix('test string', 'hello')
        'test string'
    """
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def remove_suffix(text: str, suffix: str) -> str:
    """Remove suffix from string if present.

    Args:
        text: Input string
        suffix: Suffix to remove

    Returns:
        String with suffix removed

    Examples:
        >>> remove_suffix('hello world', ' world')
        'hello'
        >>> remove_suffix('test string', 'hello')
        'test string'
    """
    if not suffix:
        return text
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text


def generate_merge_paths(paths: list[str]) -> str:
    """Generate a merged path from a list of path segments.

    Args:
        paths: List of path segments

    Returns:
        Merged path

    Examples:
        >>> generate_merge_paths(['path1', 'path2', 'file.txt'])
        'path1/path2/file.txt'
        >>> generate_merge_paths(['C:', 'Users', 'Alice'])
        'C:/Users/Alice'
    """
    if not paths:
        return ""

    # Filter out empty segments and clean up slashes
    clean_paths = []
    for path in paths:
        if path:  # Skip empty strings
            # Remove leading and trailing slashes
            clean_path = path.strip("/")
            if clean_path:
                clean_paths.append(clean_path)

    return "/".join(clean_paths)


def slugify(text: str, separator: str = "-") -> str:
    """Convert string to URL-friendly slug.

    Args:
        text: Input string
        separator: Separator character, defaults to '-'

    Returns:
        URL-friendly slug

    Examples:
        >>> slugify('Hello World!')
        'hello-world'
        >>> slugify('This is a Test!', '_')
        'this_is_a_test'
    """
    # Convert to lowercase
    text = text.lower()
    # Replace non-alphanumeric characters with separator
    text = re.sub(r"[^a-z0-9]+", separator, text)
    # Remove leading/trailing separators
    text = text.strip(separator)
    return text


def truncate(text: str, length: int, suffix: str = "...") -> str:
    """Truncate string to specified length with optional suffix.

    Args:
        text: Input string
        length: Maximum length
        suffix: Suffix to add if truncated, defaults to '...'

    Returns:
        Truncated string

    Examples:
        >>> truncate('Hello World', 5)
        'Hello...'
        >>> truncate('Hello World', 20)
        'Hello World'
        >>> truncate('Hello World', 8, '...')
        'Hello...'
    """
    if len(text) <= length:
        return text

    if length == 0:
        return suffix

    if length <= len(suffix):
        return suffix[:length]

    return text[:length] + suffix


def word_count(text: str) -> int:
    """Count words in a string.

    Args:
        text: Input string

    Returns:
        Number of words

    Examples:
        >>> word_count('Hello world')
        2
        >>> word_count('  Hello   world  test  ')
        3
        >>> word_count('')
        0
    """
    return len(text.split())


def reverse(text: str) -> str:
    """Reverse a string.

    Args:
        text: Input string

    Returns:
        Reversed string

    Examples:
        >>> reverse('hello')
        'olleh'
        >>> reverse('Python')
        'nohtyP'
    """
    return text[::-1]
