#!/usr/bin/env python3
from math import ceil, floor, exp, log
class Bloom:
    ''' Implements the basic bloom filter using bytearray and MD5 hashing
    If we let k be the number of hash functions involved, m the size of the bloom filter, n be the expected number of elemeents coming in, then
    k = (m/n) ln 2 and m = -(n ln p)/(ln 2)^2 are asymptotically optimal.
    However, as bytearrays are used, m is made divisible by eight, currently pessimistically.
    '''
    
    def hash(s, seed, m):
        ''' Compute one hash of at least m bits, returned as a bytes object of whatever length '''
        return hashlib.md5(s.encode()).digest()
        
    def khashes(s, k, m):
        ''' Make k hashes of length m from one string; return as integer list '''
        
        
    def __init__(self, n, p):
        ''' Initialize a bloom filter of n expected elements with FPR = p'''
        m = ceil(-(n * log(p))/(log(2)) ** 2 / 8) << 3
        assert(m % 8 == 0)
        k1 = floor(m / n * log(2))
        k2 = ceil(m / n * log(2))
        self.k = k1 if (1 - exp(-k1 * n / m)) ** k1 < (1 - exp(-k2 * n / m)) ** k2 else k2
        self.arr = bytearray(m // 8)

    def insert(s):
        for h in khashes(s, self.k, len(self.arr) << 3):
            self.arr[h // 8] |= 1 << h % 8

    def query(s):
        return all((self.arr[h // 8] and 1 << h % 8 for h in khashes(s, self.k, len(self.arr) << 3)))

if __name__ == "__main__":
    b = Bloom(5, 0.1)
