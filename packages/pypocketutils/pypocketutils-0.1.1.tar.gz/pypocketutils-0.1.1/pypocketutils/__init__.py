# handyutils.py

def is_palindrome(s):
    """
    Check if the input string or number is a palindrome.

    Args:
        s (str or int): The string or number to check.

    Returns:
        bool: True if palindrome, False otherwise.
    """
    s = str(s).lower()
    return s == s[::-1]

def factorial(n):
    """
    Calculate the factorial of a non-negative integer n.

    Args:
        n (int): Non-negative integer.

    Returns:
        int: Factorial of n.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Negative numbers do not have factorials.")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def fibonacci(n):
    """
    Generate a list containing first n Fibonacci numbers.

    Args:
        n (int): Number of Fibonacci numbers to generate.

    Returns:
        list: List of first n Fibonacci numbers.
    """
    if n <= 0:
        return []
    fib_seq = [0, 1]
    while len(fib_seq) < n:
        fib_seq.append(fib_seq[-1] + fib_seq[-2])
    return fib_seq[:n]

def is_prime(num):
    """
    Check if a number is prime.

    Args:
        num (int): Number to check.

    Returns:
        bool: True if prime, False otherwise.
    """
    if num <= 1:
        return False
    if num <= 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    i = 5
    while i * i <= num:
        if num % i == 0 or num % (i + 2) == 0:
            return False
        i += 6
    return True

def gcd(a, b):
    """
    Compute the Greatest Common Divisor (GCD) of two numbers using Euclid's algorithm.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: GCD of a and b.
    """
    while b:
        a, b = b, a % b
    return abs(a)

def lcm(a, b):
    """
    Compute the Least Common Multiple (LCM) of two numbers.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: LCM of a and b.
    """
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)

def sum_of_digits(n):
    """
    Calculate the sum of digits of an integer.

    Args:
        n (int): The number.

    Returns:
        int: Sum of digits.
    """
    return sum(int(digit) for digit in str(abs(n)))

def is_armstrong(n):
    """
    Check if a number is an Armstrong number.

    Args:
        n (int): Number to check.

    Returns:
        bool: True if Armstrong, False otherwise.
    """
    digits = list(map(int, str(abs(n))))
    power = len(digits)
    return sum(d ** power for d in digits) == n

def reverse_string(s):
    """
    Reverse the given string.

    Args:
        s (str): String to reverse.

    Returns:
        str: Reversed string.
    """
    return s[::-1]

def toggle_case(s):
    """
    Toggle case of each character in the string.

    Args:
        s (str): Input string.

    Returns:
        str: String with toggled case.
    """
    return ''.join(c.lower() if c.isupper() else c.upper() for c in s)

def count_vowels(s):
    """
    Count vowels in a string.

    Args:
        s (str): Input string.

    Returns:
        int: Number of vowels.
    """
    vowels = "aeiouAEIOU"
    return sum(1 for c in s if c in vowels)

def are_anagrams(s1, s2):
    """
    Check if two strings are anagrams.

    Args:
        s1 (str): First string.
        s2 (str): Second string.

    Returns:
        bool: True if anagrams, False otherwise.
    """
    return sorted(s1.replace(" ", "").lower()) == sorted(s2.replace(" ", "").lower())

def decimal_to_binary(n):
    """
    Convert a decimal number to binary string.

    Args:
        n (int): Decimal number.

    Returns:
        str: Binary representation.
    """
    return bin(n)[2:]

def decimal_to_hex(n):
    """
    Convert a decimal number to hexadecimal string.

    Args:
        n (int): Decimal number.

    Returns:
        str: Hexadecimal representation.
    """
    return hex(n)[2:]

def binary_to_decimal(b):
    """
    Convert a binary string to decimal integer.

    Args:
        b (str): Binary string.

    Returns:
        int: Decimal number.
    """
    return int(b, 2)

def hex_to_decimal(h):
    """
    Convert a hexadecimal string to decimal integer.

    Args:
        h (str): Hexadecimal string.

    Returns:
        int: Decimal number.
    """
    return int(h, 16)

def find_duplicates(lst):
    """
    Find duplicates in a list.

    Args:
        lst (list): Input list.

    Returns:
        list: List of duplicates.
    """
    seen = set()
    duplicates = set()
    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)

def flatten_list(nested_list):
    """
    Flatten a nested list of arbitrary depth.

    Args:
        nested_list (list): Nested list.

    Returns:
        list: Flattened list.
    """
    flat = []
    for item in nested_list:
        if isinstance(item, list):
            flat.extend(flatten_list(item))
        else:
            flat.append(item)
    return flat

def chunk_list(lst, chunk_size):
    """
    Split list into chunks of specified size.

    Args:
        lst (list): Input list.
        chunk_size (int): Size of each chunk.

    Returns:
        list: List of chunks (lists).
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
