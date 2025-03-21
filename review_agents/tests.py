import itertools
import time

def factorial_permutations(n):
    """Factorial time complexity O(n!)"""
    elements = list(range(n))
    count = 0
    for _ in itertools.permutations(elements):
        count += 1
    return count

n = 10  # n=10 takes significant time, n=12+ takes much longer
start = time.time()
print(f"Total permutations for {n}: {factorial_permutations(n)}")
end = time.time()
print(f"Time taken: {end - start:.4f} seconds")

