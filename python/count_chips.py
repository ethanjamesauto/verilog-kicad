
# Components below:
# ABC RESULTS:    \74AC04_6x1NOT cells:        6
# ABC RESULTS:   \74AC08_4x1AND2 cells:        4
# ABC RESULTS:   \74AC02_4x1NOR2 cells:        4
# ABC RESULTS:    \74AC32_4x1OR2 cells:        4
# ABC RESULTS:   \74AC10_3x1NAND3 cells:       3
# ABC RESULTS:   \74AC00_4x1NAND2 cells:       4
# ABC RESULTS:   \74AC20_2x1NAND4 cells:       2
# ABC RESULTS:   \74AC86_4x1XOR2 cells:        4
# ABC RESULTS:   \74AC257_4x1MUX2 cells:       4

import sys
import os
from math import ceil

if len(sys.argv) != 2:
    print('Usage: python3 count_chips.py yosys_logfile.txt')
    exit(1)

def assemble_dict(fn):
    dict = {}
    with open(fn) as f:
        for l in f.readlines():
            if (not l.startswith(' ') and 'ABC RESULTS:' in l and '74AC' in l):
                str = l[l.find('74AC'):].split(' ')
                dict[str[0]] = int(str[-1])
    return dict

dict = assemble_dict(__file__)

counts = assemble_dict(sys.argv[1])

print('IC Usage:')

cnt = 0
for key in counts.keys():
    n = ceil(counts[key] / dict[key])
    cnt += n
    print(key, ':', n, sep='\t')

print()
print('Total ICs', ':', cnt, sep='\t')