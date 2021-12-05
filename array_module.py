from array import array
from random import random

floats = array('d', (random() for _ in range(10**7)))
with open('floats.bin', 'wb') as file:
    floats.tofile(file)

floats2 = array('d')
with open('floats.bin', 'rb') as file:
    floats2.fromfile(file, 10**7)

print(floats == floats2)
