#!/usr/bin/env python3
from bloompy import Bloom
import random, sys
from math import ceil, log, floor, exp
from functools import reduce

class BlockedBloom(Bloom):
    ''' Implements a hopefully cache-friendly Bloom filter per Putze et al
    The first hash says which bloom filter to work in, then go as usual '''
    def __init__(self, k, nBytes, b):
        ''' Note that k is the number of hash functions after using one '''
        self.k = k
        self.arrs = [Bloom(k, nBytes) for i in range(b)]
        self.seeds = [1 + random.getrandbits(127) for i in range(k + 1)] #range(1 + ceil((k * nBytes << 3)/Bloom._hashLen()))]
        #self.seeds = [seed.to_bytes(ceil(seed.bit_length()), sys.byteorder) for seed in self.seeds]

    @classmethod
    def build(cls, n, p):
        ''' Initialize a bloom filter of n expected elements with FPR = p'''
        m = ceil(-n * log(p) / log(2) ** 2 / 512) << 9
        k1 = floor(m / n * log(2))
        k2 = ceil(m / n * log(2))
        k = k1 if (1 - exp(-k1 * n / m)) ** k1 < (1 - exp(-k2 * n / m)) ** k2 else k2
        
        return BlockedBloom(max(1, k - 1), 64, m // 512)

    def _hash1(self, s, b):
        ''' Returns an index in the range 0..b '''
##        hashBytes = self._hash(s, self.seeds[-1])
        return self._hash(s, self.seeds[-1]) % b

    def insert(self, s):
        h = self._hash1(s, len(self.arrs))
        self.arrs[h].insert(s)

    def query(self, s):
        h = self._hash1(s, len(self.arrs))
        return self.arrs[h].query(s)

if __name__ == "__main__":
    import pickle, argparse
    
    def cmd_build(args):
        bf = BlockedBloom.build(args.n, args.f)
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
