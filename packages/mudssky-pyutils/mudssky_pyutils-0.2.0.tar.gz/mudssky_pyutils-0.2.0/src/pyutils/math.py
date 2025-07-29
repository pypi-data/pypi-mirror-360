"""Math utility functions.

This module provides utility functions for mathematical operations,
ported from the jsutils library.
"""

from typing import TypeVar


T = TypeVar("T")


def get_random_int(min_val: int, max_val: int) -> int:
    """Generate a random integer between min and max (inclusive).

    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)

    Returns:
        Random integer between min_val and max_val

    Raises:
        ValueError: If min_val > max_val

    Examples:
        >>> result = get_random_int(1, 10)
        >>> 1 <= result <= 10
        True
        >>> get_random_int(5, 5)
        5
    """
    if min_val > max_val:
        raise ValueError("min_val must be less than or equal to max_val")

    import secrets

    return secrets.randbelow(max_val - min_val + 1) + min_val


def get_random_item_from_array(items: list[T]) -> T:
    """Get a random item from a list.

    Args:
        items: List to select from

    Returns:
        Random item from the list

    Raises:
        IndexError: If the list is empty

    Examples:
        >>> items = [1, 2, 3, 4, 5]
        >>> result = get_random_item_from_array(items)
        >>> result in items
        True
        >>> get_random_item_from_array(['apple'])
        'apple'
    """
    if not items:
        raise IndexError("Cannot select from empty list")
    import secrets

    return secrets.choice(items)


def clamp(
    value: int | float, min_val: int | float, max_val: int | float
) -> int | float:
    """Clamp a value between min and max bounds.

    Args:
        value: Value to clamp
        min_val: Minimum bound
        max_val: Maximum bound

    Returns:
        Clamped value

    Examples:
        >>> clamp(5, 1, 10)
        5
        >>> clamp(-5, 1, 10)
        1
        >>> clamp(15, 1, 10)
        10
    """
    return max(min_val, min(value, max_val))


def lerp(start: int | float, end: int | float, t: float) -> float:
    """Linear interpolation between two values.

    Args:
        start: Starting value
        end: Ending value
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated value

    Examples:
        >>> lerp(0, 10, 0.5)
        5.0
        >>> lerp(10, 20, 0.25)
        12.5
        >>> lerp(5, 15, 0.0)
        5.0
    """
    return start + (end - start) * t


def normalize(value: int | float, min_val: int | float, max_val: int | float) -> float:
    """Normalize a value to a 0-1 range based on min and max bounds.

    Args:
        value: Value to normalize
        min_val: Minimum bound
        max_val: Maximum bound

    Returns:
        Normalized value (0.0 to 1.0)

    Raises:
        ZeroDivisionError: If max_val equals min_val (zero range)

    Examples:
        >>> normalize(5, 0, 10)
        0.5
        >>> normalize(25, 0, 100)
        0.25
        >>> normalize(0, 0, 10)
        0.0
    """
    if max_val == min_val:
        raise ZeroDivisionError("Cannot normalize with zero range (max_val == min_val)")
    return (value - min_val) / (max_val - min_val)


def degrees_to_radians(degrees: int | float) -> float:
    """Convert degrees to radians.

    Args:
        degrees: Angle in degrees

    Returns:
        Angle in radians

    Examples:
        >>> import math
        >>> abs(degrees_to_radians(180) - math.pi) < 1e-10
        True
        >>> abs(degrees_to_radians(90) - math.pi/2) < 1e-10
        True
    """
    import math

    return degrees * math.pi / 180


def radians_to_degrees(radians: int | float) -> float:
    """Convert radians to degrees.

    Args:
        radians: Angle in radians

    Returns:
        Angle in degrees

    Examples:
        >>> import math
        >>> abs(radians_to_degrees(math.pi) - 180) < 1e-10
        True
        >>> abs(radians_to_degrees(math.pi/2) - 90) < 1e-10
        True
    """
    import math

    return radians * 180 / math.pi


def is_even(number: int) -> bool:
    """Check if a number is even.

    Args:
        number: Integer to check

    Returns:
        True if even, False if odd

    Examples:
        >>> is_even(4)
        True
        >>> is_even(5)
        False
        >>> is_even(0)
        True
    """
    return number % 2 == 0


def is_odd(number: int) -> bool:
    """Check if a number is odd.

    Args:
        number: Integer to check

    Returns:
        True if odd, False if even

    Examples:
        >>> is_odd(4)
        False
        >>> is_odd(5)
        True
        >>> is_odd(0)
        False
    """
    return number % 2 == 1


def gcd(a: int, b: int) -> int:
    """Calculate the greatest common divisor of two integers.

    Args:
        a: First integer
        b: Second integer

    Returns:
        Greatest common divisor

    Examples:
        >>> gcd(12, 8)
        4
        >>> gcd(17, 13)
        1
        >>> gcd(0, 5)
        5
    """
    import math

    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """Calculate the least common multiple of two integers.

    Args:
        a: First integer
        b: Second integer

    Returns:
        Least common multiple

    Examples:
        >>> lcm(12, 8)
        24
        >>> lcm(3, 5)
        15
        >>> lcm(0, 5)
        0
    """
    import math

    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)


def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer.

    Args:
        n: Non-negative integer

    Returns:
        Factorial of n

    Raises:
        ValueError: If n is negative

    Examples:
        >>> factorial(5)
        120
        >>> factorial(0)
        1
        >>> factorial(1)
        1
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")

    import math

    return math.factorial(n)


def is_prime(n: int) -> bool:
    """Check if a number is prime.

    Args:
        n: Integer to check

    Returns:
        True if prime, False otherwise

    Examples:
        >>> is_prime(7)
        True
        >>> is_prime(8)
        False
        >>> is_prime(2)
        True
        >>> is_prime(1)
        False
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    import math

    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.

    Args:
        n: Position in Fibonacci sequence (0-indexed)

    Returns:
        nth Fibonacci number

    Raises:
        ValueError: If n is negative

    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(10)
        55
    """
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")

    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def round_to_precision(value: float, precision: int) -> float:
    """Round a number to specified decimal places.

    Args:
        value: Number to round
        precision: Number of decimal places

    Returns:
        Rounded number

    Examples:
        >>> round_to_precision(3.14159, 2)
        3.14
        >>> round_to_precision(2.5, 0)
        2.0
    """
    return round(value, precision)
