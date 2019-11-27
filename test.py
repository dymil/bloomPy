#!/usr/bin/env python3
from bloompy import Bloom
from blocked_bf import BlockedBloom
import random, csv, timeit, string

def query(query_set, bf, res):
    ''' Query a bloom filter '''
    res.append(sum((bf.query(q) for q in query_set)) / len(query_set))

def runTrial(query_set, bf, bbf):
    fprs = []
    number = 1
    timeBF = timeit.timeit('query(query_set, bf, fprs)', setup="from __main__ import query",
                           globals=locals(), number=number) / number / len(query_set)
    print(timeBF)
    fprBF = fprs[0]

    fprs.clear()
    timeBBF = timeit.timeit('query(query_set, bbf, fprs)', setup="from __main__ import query",
                            globals=locals(), number=number) / number / len(query_set)
    print(timeBBF)
    fprBBF = fprs[0]
    return (timeBF, fprBF, timeBBF, fprBBF)

# Generate the set we'll be working with, adapted from
# stackoverflow.com/questions/2257441
N = 1 << 21
random.seed()
lines = set([''.join(random.choices(string.printable,
                                k=5)) for _ in range(N)])

with open('results.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=['N', 'FPR',
                    'Basic unseen time', 'Basic unseen FPR',
                    'Basic half-seen time', 'Basic half-seen FPR',
                    'Basic seen time', 'Basic seen FPR',
                    'Blocked unseen time', 'Blocked unseen FPR',
                    'Blocked half-seen time', 'Blocked half-seen FPR',
                    'Blocked seen time', 'Blocked seen FPR'])
    writer.writeheader()
    
    for trial in range(200):
        # first half is in, second is out
        in_set = random.sample(lines, random.randint(1000, N >> 1))
        fpr = random.uniform(0.01, 0.25)
        bf = Bloom.build(len(in_set), fpr)
        bbf = BlockedBloom.build(len(in_set), fpr)
        print("built!", len(in_set), fpr)
        for s in in_set:
            bf.insert(s)
            bbf.insert(s)
        print("inserted!")
        out_set = lines.difference(in_set)
        unseen = runTrial(out_set, bf, bbf)
        half_seen = runTrial(in_set + random.sample(out_set, len(in_set)), bf, bbf)
        seen = runTrial(in_set, bf, bbf)
        writer.writerow({
            'N':len(in_set), 'FPR':fpr,
            'Basic unseen time':unseen[0], 'Basic unseen FPR':unseen[1],
            'Basic half-seen time':half_seen[0], 'Basic half-seen FPR':(half_seen[1] - 0.5) * 2,
            'Basic seen time':seen[0], 'Basic seen FPR':1-seen[1],
            'Blocked unseen time':unseen[2], 'Blocked unseen FPR':unseen[3],
            'Blocked half-seen time':half_seen[2], 'Blocked half-seen FPR':(half_seen[3] - 0.5) * 2,
            'Blocked seen time':seen[2], 'Blocked seen FPR':1-seen[3]})
