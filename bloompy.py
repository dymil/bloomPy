#!/usr/bin/env python3
from math import ceil, floor, exp, log
from functools import reduce
from operator import add
import hashlib, sys

class Bloom:
    ''' Implements the basic bloom filter using bytearray and BLAKE hashing
    If k is the number of hashes, m the size of the bloom filter, and n the expected number of elemeents, then
    k = (m/n) ln 2 and m = -(n ln p)/(ln 2)^2 are asymptotically optimal.
    However, as bytearrays are used, m is made divisible by eight, currently pessimistically.
    '''    
    def __init__(self, n, p):
        ''' Initialize a bloom filter of n expected elements with FPR = p'''
        m = ceil(-n * log(p)/(log(2)) ** 2 / 8) << 3
        assert(m % 8 == 0)
        k1 = floor(m / n * log(2))
        k2 = ceil(m / n * log(2))
        self.k = k1 if (1 - exp(-k1 * n / m)) ** k1 < (1 - exp(-k2 * n / m)) ** k2 else k2
        self.arr = bytearray(m >> 3)

    _hashLen = 128
    
    def _hash(s, seed):
        ''' Compute one hash, returned as a bytes object of whatever length '''
        return hashlib.blake2b(s.encode(), person=seed).digest()
        
    def _khashes(s, k, m):
        ''' Make k hashes modulo m from one string; return as integer list
        This is currently done by computing as many hashes as needed to get k indices.
        A more-efficient alternative would be using
        Kirsch, A. and Mitzenmacher, M. (2008), Less hashing, same performance: Building a better Bloom filter.
        Random Struct. Alg., 33: 187-218. doi:10.1002/rsa.20208'''
        hashBytes = [x for x in Bloom._hash(s, (0).to_bytes(1, sys.byteorder))]
        hashBytes += [x for i in range(1, ceil(m / Bloom._hashLen)) for x in Bloom._hash(s, i.to_bytes(log(i, 2) / 8, sys.byteorder))]
        return [reduce(lambda acc, x: (acc + x) % m,
                       (hashBytes[i + j] << (j << 3) for j in range(ceil(m / (8 * 256)))),
                       0) for i in range(k)]

    def insert(self, s):
        for h in Bloom._khashes(s, self.k, len(self.arr) << 3):
            self.arr[h >> 3] |= 1 << h % 8

    def query(self, s):
        return all((self.arr[h // 8] and 1 << h % 8 for h in Bloom._khashes(s, self.k, len(self.arr) << 3)))

if __name__ == "__main__":
    b = Bloom(10, 0.1)
    b.insert("hello")
    print(b.query('hello'))
    print(b.query('goodbye'))
