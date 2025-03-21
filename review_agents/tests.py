import time
import sys
sys.setrecursionlimit(3000)  # Increase recursion limit for deep recursion

def ackermann(m, n):
    """Ackermann function, grows faster than exponential"""
    if m == 0:
        return n + 1
    elif m > 0 and n == 0:
        return ackermann(m - 1, 1)
    else:
        return ackermann(m - 1, ackermann(m, n - 1))

m, n = 3, 8  # Values causing extreme growth
start = time.time()
print(f"Ackermann({m}, {n}) = {ackermann(m, n)}")
end = time.time()
print(f"Time taken: {end - start:.4f} seconds")
