import numpy as np

a = np.arange(1, 11)

alpha = (1 + np.sqrt(5)) / 2
beta = (1 - np.sqrt(5)) / 2

fib_nums = np.rint(((alpha ** a) - (beta ** a)) / (np.sqrt(5)))
print(f"The first {len(a)} numbers of Fibonacci series are {fib_nums}.")
