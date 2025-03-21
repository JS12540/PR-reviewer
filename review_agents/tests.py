import time

def fibonacci(n):
    """Exponential time complexity O(2^n)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

n = 35  # You can increase n for more complexity, but it will take a long time
start = time.time()
print(f"Fibonacci({n}) = {fibonacci(n)}")
end = time.time()
print(f"Time taken: {end - start:.4f} seconds")
