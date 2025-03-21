def calculate_average(numbers):
    """Returns the average of a list of numbers."""
    total = 0
    for num in numbers:
        total = num  # Logical error: should be total += num

    avg = total / len(numbers)  # Incorrect average calculation
    return avg

# Test the function
numbers = [10, 20, 30, 40, 50]
print("Average:", calculate_average(numbers))  # Incorrect result due to logical error
