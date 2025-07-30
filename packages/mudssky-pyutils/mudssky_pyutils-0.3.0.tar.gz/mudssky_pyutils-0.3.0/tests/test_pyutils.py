#!/usr/bin/env python

"""Integration tests for pyutils package."""

import pytest

from pyutils import array, async_utils, bytes, function, math, object, string


class TestPackageIntegration:
    """Test package-level integration."""

    def test_package_imports(self):
        """Test that all modules can be imported."""
        # Test that all main modules are available
        assert hasattr(array, "chunk")
        assert hasattr(string, "camel_case")
        assert hasattr(math, "clamp")
        assert hasattr(object, "get")
        assert hasattr(function, "memoize")
        assert hasattr(async_utils, "delay")
        assert hasattr(bytes, "to_base64")

    def test_cross_module_functionality(self):
        """Test functionality that spans multiple modules."""
        # Test array and string integration
        words = ["hello", "world", "test"]
        chunked = array.chunk(words, 2)
        assert len(chunked) == 2

        # Convert to camel case
        camel_words = [string.camel_case(word) for word in words]
        assert camel_words == ["hello", "world", "test"]

    def test_object_and_array_integration(self):
        """Test object and array module integration."""
        data = [
            {"name": "Alice", "age": 30, "city": "New York"},
            {"name": "Bob", "age": 25, "city": "London"},
            {"name": "Charlie", "age": 35, "city": "Tokyo"},
        ]

        # Group by city using object.get and array functions
        cities = [object.get(item, "city") for item in data]
        unique_cities = array.unique(cities)
        assert len(unique_cities) == 3

        # Get max age using array.max_by and object.get
        oldest = array.max_by(data, lambda x: object.get(x, "age"))
        assert object.get(oldest, "name") == "Charlie"

    def test_string_and_bytes_integration(self):
        """Test string and bytes module integration."""
        # Test string processing with bytes encoding
        text = "Hello, 世界! 🌍"

        # Convert to slug and encode
        slug = string.slugify(text)
        encoded = bytes.to_base64(slug)
        decoded = bytes.from_base64(encoded)

        assert decoded == slug
        assert isinstance(encoded, str)

    def test_math_and_array_integration(self):
        """Test math and array module integration."""
        numbers = [1, 5, 10, 15, 20]

        # Clamp all numbers to range [5, 15]
        clamped = [math.clamp(n, 5, 15) for n in numbers]
        assert clamped == [5, 5, 10, 15, 15]

        # Use array functions with math operations
        sum_result = array.sum_by(numbers, lambda x: math.clamp(x, 0, 10))
        assert sum_result == 36  # 1 + 5 + 10 + 10 + 10

    @pytest.mark.asyncio
    async def test_async_and_function_integration(self):
        """Test async_utils and function module integration."""
        # Create a memoized async function
        call_count = 0

        @function.memoize
        async def expensive_async_operation(x):
            nonlocal call_count
            call_count += 1
            result = await async_utils.delay(x * 2, 0.01)
            return result

        # First call
        result1 = await expensive_async_operation(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with same argument - should use cache
        result2 = await expensive_async_operation(5)
        assert result2 == 10
        assert call_count == 1  # No additional call

    @pytest.mark.asyncio
    async def test_async_array_processing(self):
        """Test async processing of arrays."""
        numbers = [1, 2, 3, 4, 5]

        # Async map with delay
        async def double_with_delay(x):
            return await async_utils.delay(x * 2, 0.01)

        results = await async_utils.map_async(double_with_delay, numbers)
        assert results == [2, 4, 6, 8, 10]

        # Combine with array functions
        chunked_results = array.chunk(results, 2)
        assert len(chunked_results) == 3
        assert chunked_results[0] == [2, 4]

    def test_complex_data_processing_pipeline(self):
        """Test a complex data processing pipeline using multiple modules."""
        # Sample data
        raw_data = [
            "  John Doe - Software Engineer  ",
            "  jane_smith - Product Manager  ",
            "  bob-wilson - Data Scientist  ",
            "  alice.brown - UX Designer  ",
        ]

        # Processing pipeline
        processed = []
        for item in raw_data:
            # Clean and split
            cleaned = string.trim(item)
            parts = cleaned.split(" - ")

            if len(parts) == 2:
                name, role = parts

                # Process name
                name_slug = string.slugify(name)
                name_camel = string.camel_case(name.replace(" ", "_"))

                # Process role
                role_snake = string.snake_case(role)

                # Create object
                person = {
                    "original_name": name,
                    "name_slug": name_slug,
                    "name_camel": name_camel,
                    "role": role,
                    "role_snake": role_snake,
                    "id": string.generate_uuid()[:8],
                }

                processed.append(person)

        # Verify processing
        assert len(processed) == 4

        # Check specific transformations
        john = array.first(processed, lambda x: "john" in x["name_slug"])
        assert john is not None
        assert john["name_slug"] == "john-doe"
        assert john["role_snake"] == "software_engineer"

        # Group by role using object functions
        roles = array.unique([object.get(p, "role") for p in processed])
        assert len(roles) == 4

        # Test object manipulation
        for person in processed:
            # Add computed fields
            object.set_value(
                person, "display_name", string.capitalize(person["original_name"])
            )
            object.set_value(person, "short_id", person["id"][:4])

        # Verify all have new fields
        assert all(object.has(p, "display_name") for p in processed)
        assert all(object.has(p, "short_id") for p in processed)

    def test_error_handling_across_modules(self):
        """Test error handling consistency across modules."""
        # Test that modules handle edge cases consistently

        # Empty data
        assert array.chunk([], 2) == []
        assert string.trim("") == ""
        assert object.get({}, "nonexistent") is None

        # Invalid inputs
        with pytest.raises((ValueError, TypeError)):
            math.clamp("not_a_number", 0, 10)

        with pytest.raises((ValueError, TypeError)):
            array.chunk([1, 2, 3], 0)  # Invalid chunk size

    def test_performance_integration(self):
        """Test performance characteristics of integrated operations."""
        import time

        # Large dataset
        large_data = list(range(1000))

        # Time array operations
        start_time = time.time()
        chunked = array.chunk(large_data, 50)
        chunk_time = time.time() - start_time

        assert len(chunked) == 20
        assert chunk_time < 0.1  # Should be fast

        # Time string operations
        strings = [f"item_{i}" for i in range(100)]
        start_time = time.time()
        camel_strings = [string.camel_case(s) for s in strings]
        string_time = time.time() - start_time

        assert len(camel_strings) == 100
        assert string_time < 0.1  # Should be fast

        # Test memoization performance
        @function.memoize
        def fibonacci_memo(n):
            if n <= 1:
                return n
            return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)

        start_time = time.time()
        result = fibonacci_memo(30)
        memo_time = time.time() - start_time

        assert result == 832040
        assert memo_time < 0.01  # Memoization should make this very fast


class TestModuleCompatibility:
    """Test compatibility between different module versions and Python versions."""

    def test_python_version_compatibility(self):
        """Test that code works across Python versions."""
        import sys

        # Test that we're using features compatible with our target Python version
        assert sys.version_info >= (3, 6), "Requires Python 3.6+"

        # Test type hints work (Python 3.5+)

        def typed_function(items: list[str]) -> dict[str, int]:
            return {item: len(item) for item in items}

        result = typed_function(["hello", "world"])
        assert result == {"hello": 5, "world": 5}

    def test_import_structure(self):
        """Test that import structure is consistent."""
        # Test that we can import from package root

        # Test that submodules are accessible
        from pyutils import array as arr_module
        from pyutils import string as str_module

        assert hasattr(arr_module, "chunk")
        assert hasattr(str_module, "camel_case")

    def test_no_circular_imports(self):
        """Test that there are no circular import dependencies."""
        # This test passes if we can import all modules without errors
        try:
            from pyutils import (
                array,
                async_utils,
                bytes,
                function,
                math,
                object,
                string,
            )

            # Use the imports to avoid unused import warnings
            modules = [array, string, math, object, function, async_utils, bytes]
            # If we get here, no circular imports
            assert len(modules) == 7
        except ImportError as e:
            pytest.fail(f"Circular import detected: {e}")


@pytest.fixture
def sample_data():
    """Provide sample data for integration tests."""
    return {
        "users": [
            {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "age": 28},
            {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "age": 34},
            {
                "id": 3,
                "name": "Charlie Brown",
                "email": "charlie@example.com",
                "age": 22,
            },
        ],
        "products": [
            {
                "id": 101,
                "name": "Laptop Computer",
                "price": 999.99,
                "category": "Electronics",
            },
            {
                "id": 102,
                "name": "Office Chair",
                "price": 299.50,
                "category": "Furniture",
            },
            {
                "id": 103,
                "name": "Coffee Maker",
                "price": 79.99,
                "category": "Appliances",
            },
        ],
    }


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_data_transformation_scenario(self, sample_data):
        """Test a realistic data transformation scenario."""
        users = sample_data["users"]

        # Transform user data
        transformed_users = []
        for user in users:
            # Create slug from name
            name_slug = string.slugify(object.get(user, "name", ""))

            # Create display name
            display_name = string.capitalize(object.get(user, "name", ""))

            # Clamp age to reasonable range
            age = math.clamp(object.get(user, "age", 0), 18, 100)

            # Create new user object
            new_user = object.merge(
                user,
                {
                    "name_slug": name_slug,
                    "display_name": display_name,
                    "age_clamped": age,
                    "email_hash": bytes.get_hash(object.get(user, "email", "")),
                },
            )

            transformed_users.append(new_user)

        # Verify transformations
        assert len(transformed_users) == 3

        alice = array.first(
            transformed_users, lambda u: object.get(u, "name_slug") == "alice-johnson"
        )
        assert alice is not None
        assert object.get(alice, "display_name") == "Alice Johnson"
        assert object.has(alice, "email_hash")

    @pytest.mark.asyncio
    async def test_async_data_processing_scenario(self, sample_data):
        """Test async data processing scenario."""
        products = sample_data["products"]

        # Simulate async API calls for each product
        async def enrich_product(product):
            # Simulate API delay
            await async_utils.delay(None, 0.01)

            # Add computed fields
            enriched = object.clone(product)
            object.set_value(
                enriched, "name_slug", string.slugify(object.get(product, "name", ""))
            )
            object.set_value(
                enriched,
                "price_rounded",
                math.round_to_precision(object.get(product, "price", 0), 0),
            )
            object.set_value(
                enriched,
                "category_snake",
                string.snake_case(object.get(product, "category", "")),
            )

            return enriched

        # Process all products concurrently
        enriched_products = await async_utils.map_async(enrich_product, products)

        # Verify results
        assert len(enriched_products) == 3

        laptop = array.first(
            enriched_products, lambda p: "laptop" in object.get(p, "name_slug", "")
        )
        assert laptop is not None
        assert object.get(laptop, "price_rounded") == 1000
        assert object.get(laptop, "category_snake") == "electronics"

    def test_configuration_processing_scenario(self):
        """Test configuration file processing scenario."""
        # Simulate configuration data
        config_text = """
        # Database Configuration
        DB_HOST = localhost
        DB_PORT = 5432
        DB_NAME = myapp_db

        # API Configuration
        API_BASE_URL = https://api.example.com/v1
        API_TIMEOUT = 30
        API_RETRIES = 3
        """

        # Parse configuration
        lines = [string.trim(line) for line in config_text.split("\n")]
        config_lines = array.filter_list(
            lines, lambda line: line and not line.startswith("#")
        )

        config = {}
        for line in config_lines:
            if "=" in line:
                key, value = line.split("=", 1)
                key = string.trim(key)
                value = string.trim(value)

                # Convert to appropriate types
                if value.isdigit():
                    value = int(value)
                elif value.lower() in ("true", "false"):
                    value = value.lower() == "true"

                object.set_value(config, key, value)

        # Verify parsing
        assert object.get(config, "DB_HOST") == "localhost"
        assert object.get(config, "DB_PORT") == 5432
        assert object.get(config, "API_TIMEOUT") == 30

        # Group by prefix
        db_config = object.filter_dict(config, lambda k, v: k.startswith("DB_"))
        api_config = object.filter_dict(config, lambda k, v: k.startswith("API_"))

        assert len(db_config) == 3
        assert len(api_config) == 3

    def test_data_validation_scenario(self):
        """Test data validation scenario."""
        # Sample form data
        form_data = {
            "username": "  john_doe123  ",
            "email": "JOHN.DOE@EXAMPLE.COM",
            "age": "25",
            "bio": "Hello, I am a software developer! 🚀",
            "tags": "python,javascript,react,node.js",
        }

        # Validation and normalization
        validated_data = {}

        # Username: trim, lowercase, validate format
        username = string.trim(object.get(form_data, "username", ""))
        username = username.lower()
        if len(username) >= 3 and username.replace("_", "").isalnum():
            object.set_value(validated_data, "username", username)

        # Email: trim, lowercase
        email = string.trim(object.get(form_data, "email", ""))
        email = email.lower()
        if "@" in email and "." in email:
            object.set_value(validated_data, "email", email)

        # Age: convert to int, clamp
        try:
            age = int(object.get(form_data, "age", "0"))
            age = math.clamp(age, 13, 120)
            object.set_value(validated_data, "age", age)
        except ValueError:
            pass

        # Bio: trim, truncate
        bio = string.trim(object.get(form_data, "bio", ""))
        bio = string.truncate(bio, 200)
        object.set_value(validated_data, "bio", bio)

        # Tags: split, clean, unique
        tags_str = object.get(form_data, "tags", "")
        tags = [string.trim(tag) for tag in tags_str.split(",")]
        tags = array.unique([tag for tag in tags if tag])
        object.set_value(validated_data, "tags", tags)

        # Verify validation
        assert object.get(validated_data, "username") == "john_doe123"
        assert object.get(validated_data, "email") == "john.doe@example.com"
        assert object.get(validated_data, "age") == 25
        assert len(object.get(validated_data, "tags", [])) == 4
        assert "python" in object.get(validated_data, "tags", [])
