import numpy as np

new_array = np.empty((5,5))
new_array[:,:] = 1

print("abababa")



def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

print(new_array)