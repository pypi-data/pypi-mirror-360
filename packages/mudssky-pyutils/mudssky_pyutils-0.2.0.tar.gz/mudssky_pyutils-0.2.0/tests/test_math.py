#!/usr/bin/env python

"""Tests for math module."""

import math

import pytest

from pyutils.math import (
    clamp,
    degrees_to_radians,
    factorial,
    fibonacci,
    gcd,
    get_random_int,
    get_random_item_from_array,
    is_even,
    is_odd,
    is_prime,
    lcm,
    lerp,
    normalize,
    radians_to_degrees,
    round_to_precision,
)


class TestClamp:
    """Test clamp function."""

    def test_clamp_within_range(self):
        """Test clamp with value within range."""
        assert clamp(5, 0, 10) == 5
        assert clamp(7.5, 0.0, 10.0) == 7.5

    def test_clamp_below_min(self):
        """Test clamp with value below minimum."""
        assert clamp(-5, 0, 10) == 0
        assert clamp(-2.5, 0.0, 10.0) == 0.0

    def test_clamp_above_max(self):
        """Test clamp with value above maximum."""
        assert clamp(15, 0, 10) == 10
        assert clamp(12.5, 0.0, 10.0) == 10.0

    def test_clamp_at_boundaries(self):
        """Test clamp with values at boundaries."""
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10

    def test_clamp_negative_range(self):
        """Test clamp with negative range."""
        assert clamp(-5, -10, -1) == -5
        assert clamp(-15, -10, -1) == -10
        assert clamp(0, -10, -1) == -1


class TestLerp:
    """Test lerp function."""

    def test_lerp_basic(self):
        """Test basic linear interpolation."""
        assert lerp(0, 10, 0.5) == 5.0
        assert lerp(0, 100, 0.25) == 25.0

    def test_lerp_boundaries(self):
        """Test lerp at boundaries."""
        assert lerp(0, 10, 0.0) == 0.0
        assert lerp(0, 10, 1.0) == 10.0

    def test_lerp_negative_values(self):
        """Test lerp with negative values."""
        assert lerp(-10, 10, 0.5) == 0.0
        assert lerp(-5, -1, 0.5) == -3.0

    def test_lerp_extrapolation(self):
        """Test lerp with values outside [0,1]."""
        assert lerp(0, 10, 1.5) == 15.0
        assert lerp(0, 10, -0.5) == -5.0

    def test_lerp_same_values(self):
        """Test lerp with same start and end values."""
        assert lerp(5, 5, 0.5) == 5.0
        assert lerp(5, 5, 0.0) == 5.0
        assert lerp(5, 5, 1.0) == 5.0


class TestNormalize:
    """Test normalize function."""

    def test_normalize_basic(self):
        """Test basic normalization."""
        assert normalize(5, 0, 10) == 0.5
        assert normalize(25, 0, 100) == 0.25

    def test_normalize_boundaries(self):
        """Test normalize at boundaries."""
        assert normalize(0, 0, 10) == 0.0
        assert normalize(10, 0, 10) == 1.0

    def test_normalize_negative_range(self):
        """Test normalize with negative range."""
        assert normalize(-5, -10, 0) == 0.5
        assert normalize(-2.5, -10, 0) == 0.75

    def test_normalize_outside_range(self):
        """Test normalize with value outside range."""
        assert normalize(15, 0, 10) == 1.5
        assert normalize(-5, 0, 10) == -0.5

    def test_normalize_zero_range(self):
        """Test normalize with zero range."""
        with pytest.raises(ZeroDivisionError):
            normalize(5, 5, 5)


class TestRoundToPrecision:
    """Test round_to_precision function."""

    def test_round_to_precision_basic(self):
        """Test basic precision rounding."""
        assert round_to_precision(3.14159, 2) == 3.14
        assert round_to_precision(3.14159, 4) == 3.1416

    def test_round_to_precision_zero_precision(self):
        """Test rounding to zero precision."""
        assert round_to_precision(3.14159, 0) == 3.0
        assert round_to_precision(3.7, 0) == 4.0

    def test_round_to_precision_negative_precision(self):
        """Test rounding with negative precision."""
        assert round_to_precision(1234.5, -1) == 1230.0
        assert round_to_precision(1234.5, -2) == 1200.0

    def test_round_to_precision_integer(self):
        """Test rounding integer values."""
        assert round_to_precision(5, 2) == 5.0
        assert round_to_precision(10, 1) == 10.0

    def test_round_to_precision_negative_numbers(self):
        """Test rounding negative numbers."""
        assert round_to_precision(-3.14159, 2) == -3.14
        assert round_to_precision(-3.7, 0) == -4.0


class TestDegreesToRadians:
    """Test degrees_to_radians function."""

    def test_degrees_to_radians_basic(self):
        """Test basic degree to radian conversion."""
        assert abs(degrees_to_radians(180) - math.pi) < 1e-10
        assert abs(degrees_to_radians(90) - math.pi / 2) < 1e-10

    def test_degrees_to_radians_zero(self):
        """Test conversion of zero degrees."""
        assert degrees_to_radians(0) == 0.0

    def test_degrees_to_radians_full_circle(self):
        """Test conversion of full circle."""
        assert abs(degrees_to_radians(360) - 2 * math.pi) < 1e-10

    def test_degrees_to_radians_negative(self):
        """Test conversion of negative degrees."""
        assert abs(degrees_to_radians(-90) - (-math.pi / 2)) < 1e-10

    def test_degrees_to_radians_fractional(self):
        """Test conversion of fractional degrees."""
        assert abs(degrees_to_radians(45) - math.pi / 4) < 1e-10


class TestRadiansToDegrees:
    """Test radians_to_degrees function."""

    def test_radians_to_degrees_basic(self):
        """Test basic radian to degree conversion."""
        assert abs(radians_to_degrees(math.pi) - 180) < 1e-10
        assert abs(radians_to_degrees(math.pi / 2) - 90) < 1e-10

    def test_radians_to_degrees_zero(self):
        """Test conversion of zero radians."""
        assert radians_to_degrees(0) == 0.0

    def test_radians_to_degrees_full_circle(self):
        """Test conversion of full circle in radians."""
        assert abs(radians_to_degrees(2 * math.pi) - 360) < 1e-10

    def test_radians_to_degrees_negative(self):
        """Test conversion of negative radians."""
        assert abs(radians_to_degrees(-math.pi / 2) - (-90)) < 1e-10

    def test_radians_to_degrees_fractional(self):
        """Test conversion of fractional radians."""
        assert abs(radians_to_degrees(math.pi / 4) - 45) < 1e-10


class TestGcd:
    """Test gcd function."""

    def test_gcd_basic(self):
        """Test basic GCD calculation."""
        assert gcd(12, 8) == 4
        assert gcd(15, 25) == 5

    def test_gcd_coprime(self):
        """Test GCD of coprime numbers."""
        assert gcd(7, 11) == 1
        assert gcd(13, 17) == 1

    def test_gcd_same_numbers(self):
        """Test GCD of same numbers."""
        assert gcd(5, 5) == 5
        assert gcd(12, 12) == 12

    def test_gcd_with_zero(self):
        """Test GCD with zero."""
        assert gcd(5, 0) == 5
        assert gcd(0, 7) == 7

    def test_gcd_negative_numbers(self):
        """Test GCD with negative numbers."""
        assert gcd(-12, 8) == 4
        assert gcd(12, -8) == 4
        assert gcd(-12, -8) == 4


class TestLcm:
    """Test lcm function."""

    def test_lcm_basic(self):
        """Test basic LCM calculation."""
        assert lcm(4, 6) == 12
        assert lcm(15, 25) == 75

    def test_lcm_coprime(self):
        """Test LCM of coprime numbers."""
        assert lcm(7, 11) == 77
        assert lcm(3, 5) == 15

    def test_lcm_same_numbers(self):
        """Test LCM of same numbers."""
        assert lcm(5, 5) == 5
        assert lcm(12, 12) == 12

    def test_lcm_with_one(self):
        """Test LCM with one."""
        assert lcm(5, 1) == 5
        assert lcm(1, 7) == 7

    def test_lcm_negative_numbers(self):
        """Test LCM with negative numbers."""
        assert lcm(-4, 6) == 12
        assert lcm(4, -6) == 12
        assert lcm(-4, -6) == 12


class TestFactorial:
    """Test factorial function."""

    def test_factorial_basic(self):
        """Test basic factorial calculation."""
        assert factorial(0) == 1
        assert factorial(1) == 1
        assert factorial(5) == 120
        assert factorial(6) == 720

    def test_factorial_larger_numbers(self):
        """Test factorial of larger numbers."""
        assert factorial(10) == 3628800

    def test_factorial_negative(self):
        """Test factorial with negative number."""
        with pytest.raises(ValueError):
            factorial(-1)

    def test_factorial_non_integer(self):
        """Test factorial with non-integer."""
        with pytest.raises(TypeError):
            factorial(3.5)


class TestFibonacci:
    """Test fibonacci function."""

    def test_fibonacci_basic(self):
        """Test basic Fibonacci calculation."""
        assert fibonacci(0) == 0
        assert fibonacci(1) == 1
        assert fibonacci(2) == 1
        assert fibonacci(3) == 2
        assert fibonacci(4) == 3
        assert fibonacci(5) == 5
        assert fibonacci(6) == 8

    def test_fibonacci_larger_numbers(self):
        """Test Fibonacci of larger numbers."""
        assert fibonacci(10) == 55
        assert fibonacci(15) == 610

    def test_fibonacci_negative(self):
        """Test Fibonacci with negative number."""
        with pytest.raises(ValueError):
            fibonacci(-1)

    def test_fibonacci_non_integer(self):
        """Test Fibonacci with non-integer."""
        with pytest.raises(TypeError):
            fibonacci(3.5)


class TestIsPrime:
    """Test is_prime function."""

    def test_is_prime_basic(self):
        """Test basic prime number checking."""
        assert is_prime(2) is True
        assert is_prime(3) is True
        assert is_prime(5) is True
        assert is_prime(7) is True
        assert is_prime(11) is True

    def test_is_prime_composite(self):
        """Test composite number checking."""
        assert is_prime(4) is False
        assert is_prime(6) is False
        assert is_prime(8) is False
        assert is_prime(9) is False
        assert is_prime(10) is False

    def test_is_prime_edge_cases(self):
        """Test edge cases for prime checking."""
        assert is_prime(0) is False
        assert is_prime(1) is False

    def test_is_prime_negative(self):
        """Test prime checking with negative numbers."""
        assert is_prime(-2) is False
        assert is_prime(-5) is False

    def test_is_prime_larger_numbers(self):
        """Test prime checking with larger numbers."""
        assert is_prime(97) is True
        assert is_prime(100) is False
        assert is_prime(101) is True


class TestIsEven:
    """Test is_even function."""

    def test_is_even_basic(self):
        """Test basic even number checking."""
        assert is_even(0) is True
        assert is_even(2) is True
        assert is_even(4) is True
        assert is_even(100) is True

    def test_is_even_odd_numbers(self):
        """Test even checking with odd numbers."""
        assert is_even(1) is False
        assert is_even(3) is False
        assert is_even(5) is False
        assert is_even(99) is False

    def test_is_even_negative(self):
        """Test even checking with negative numbers."""
        assert is_even(-2) is True
        assert is_even(-4) is True
        assert is_even(-1) is False
        assert is_even(-3) is False


class TestIsOdd:
    """Test is_odd function."""

    def test_is_odd_basic(self):
        """Test basic odd number checking."""
        assert is_odd(1) is True
        assert is_odd(3) is True
        assert is_odd(5) is True
        assert is_odd(99) is True

    def test_is_odd_even_numbers(self):
        """Test odd checking with even numbers."""
        assert is_odd(0) is False
        assert is_odd(2) is False
        assert is_odd(4) is False
        assert is_odd(100) is False

    def test_is_odd_negative(self):
        """Test odd checking with negative numbers."""
        assert is_odd(-1) is True
        assert is_odd(-3) is True
        assert is_odd(-2) is False
        assert is_odd(-4) is False


class TestGetRandomInt:
    """Test get_random_int function."""

    def test_get_random_int_range(self):
        """Test that get_random_int returns value in range."""
        for _ in range(100):  # Test multiple times
            result = get_random_int(1, 10)
            assert 1 <= result <= 10
            assert isinstance(result, int)

    def test_get_random_int_single_value(self):
        """Test get_random_int with same min and max."""
        result = get_random_int(5, 5)
        assert result == 5

    def test_get_random_int_negative_range(self):
        """Test get_random_int with negative range."""
        for _ in range(100):
            result = get_random_int(-10, -1)
            assert -10 <= result <= -1

    def test_get_random_int_zero_range(self):
        """Test get_random_int with range including zero."""
        for _ in range(100):
            result = get_random_int(-5, 5)
            assert -5 <= result <= 5

    def test_get_random_int_invalid_range(self):
        """Test get_random_int with invalid range."""
        with pytest.raises(ValueError):
            get_random_int(10, 1)


class TestGetRandomItemFromArray:
    """Test get_random_item_from_array function."""

    def test_get_random_item_basic(self):
        """Test basic random item selection."""
        items = [1, 2, 3, 4, 5]
        for _ in range(100):  # Test multiple times
            result = get_random_item_from_array(items)
            assert result in items

    def test_get_random_item_single_element(self):
        """Test random item from single element array."""
        items = [42]
        result = get_random_item_from_array(items)
        assert result == 42

    def test_get_random_item_strings(self):
        """Test random item selection with strings."""
        items = ["apple", "banana", "cherry"]
        for _ in range(50):
            result = get_random_item_from_array(items)
            assert result in items

    def test_get_random_item_empty_array(self):
        """Test random item from empty array."""
        with pytest.raises(IndexError):
            get_random_item_from_array([])

    def test_get_random_item_mixed_types(self):
        """Test random item selection with mixed types."""
        items = [1, "hello", 3.14, True]
        for _ in range(50):
            result = get_random_item_from_array(items)
            assert result in items
