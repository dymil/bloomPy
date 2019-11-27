#!/usr/bin/env python3
from math import ceil, floor, exp, log
from functools import reduce
import sys, random
from spooky import hash64

class Bloom:
    ''' Implements the basic bloom filter using bytearray and BLAKE hashing
    If k is the number of hashes, m the size of the bloom filter, and n the expected number of elemeents, then
    k = (m/n) ln 2 and m = -(n ln p)/(ln 2)^2 are asymptotically optimal.
    However, as bytearrays are used, m is made divisible by eight, currently pessimistically.
    '''
    @classmethod
    def _hashLen(cls):
        return 64
    
    def __init__(self, k, nBytes):
        self.k = k
        self.arr = bytearray(nBytes)
        random.seed()
        self.seeds = [1 + random.getrandbits(63) for i in range(k)]
                      #range(k * ceil((nBytes << 3)/(1 << Bloom._hashLen())))]
        # spookyhash64 takes as many 64 bits of seed
        #self.seeds = [seed.to_bytes(ceil(seed.bit_length() / 8), sys.byteorder) for seed in self.seeds]

    @classmethod
    def build(cls, n, p):
        ''' Initialize a bloom filter of n expected elements with FPR = p'''
        m = ceil(-n * log(p) / log(2) ** 2 / 8) << 3
        assert(m % 8 == 0)
        k1 = floor(m / n * log(2))
        k2 = ceil(m / n * log(2))
        k = k1 if (1 - exp(-k1 * n / m)) ** k1 < (1 - exp(-k2 * n / m)) ** k2 else k2
        return Bloom(k, m >> 3)

    @classmethod
    def _hash(cls, s, seed):
        ''' Compute one hash, returned as a bytes object of whatever length '''
        res = hash64(s, seed)
        return res#.to_bytes(ceil(res.bit_length() / 8), sys.byteorder)

    def _khashes(self, s, k, m):
        ''' Make k hashes modulo m from one string; return as integer list
        This is currently done by computing as many hashes as needed to get k indices.
        A more-efficient alternative would be using
        Kirsch, A. and Mitzenmacher, M. (2008), Less hashing, same performance: Building a better Bloom filter.
        Random Struct. Alg., 33: 187-218. doi:10.1002/rsa.20208'''
        return [self._hash(s, self.seeds[i]) % m for i in range(k)]
        #return [int.from_bytes(self._hash(s, self.seeds[i]), sys.byteorder) % m for i in range(k)]
        
    def insert(self, s):
        for h in self._khashes(s, self.k, len(self.arr) << 3):
            self.arr[h >> 3] |= 1 << h % 8

    def query(self, s):
        return all((self.arr[h >> 3] & (1 << h % 8) for h in self._khashes(s, self.k, len(self.arr) << 3)))

if __name__ == "__main__":
    import pickle, argparse
    
    def cmd_build(args):
        bf = Bloom.build(args.n, args.f)
        with open(args.k) as keyfile:
            for key in keyfile:
                bf.insert(key.rstrip())
        pickle.dump(bf, open(args.o, 'wb'))

    def cmd_query(args):
        bf = pickle.load(open(args.i, 'rb'))
        with open(args.q) as queryfile:
            for query in queryfile:
                query = query.rstrip()
                print(query, "Y" if bf.query(query) else "N", sep=':')

    parser = argparse.ArgumentParser(prog='bf')
    subparsers = parser.add_subparsers(title='commands', help='sub-command help')

    parser_build = subparsers.add_parser('build')
    parser_build.add_argument("-k", help="key file", required=True)
    parser_build.add_argument("-f", help="fpr", type=float, required=True)
    parser_build.add_argument("-n", help="num. distinct keys", type=int, required=True)
    parser_build.add_argument("-o", help="output file", default="bf.out")
    parser_build.set_defaults(func=cmd_build)

    parser_query = subparsers.add_parser('query')
    parser_query.add_argument("-i", help="input file", required=True)
    parser_query.add_argument("-q", help="query file", required=True)
    parser_query.set_defaults(func=cmd_query)
    args = parser.parse_args()
    args.func(args)
