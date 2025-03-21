def is_palindrome(word):
    """Checks if a word is a palindrome."""
    reversed_word = word  # Logical error: Should reverse the word, but it doesn't
    return word == reversed_word

# Test cases
print(is_palindrome("racecar"))  # Should be True, but it will return False
print(is_palindrome("hello"))    # Should be False, will return False (by coincidence)

