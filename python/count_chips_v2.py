
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
            if not l.startswith(' ') and 'ABC RESULTS:' in l and '74AC' in l:
                str = l[l.find('74AC'):].split(' ')
                partstr = str[0]
                flopcnt = int(str[-1])
            elif '$_DFF_P_ cells to' in l:
                str = l.strip().split(' ')
                partstr = str[5][1:]
                flopcnt = int(str[1])
            else:
                continue

            if partstr in dict.keys():
                dict[partstr] += flopcnt
            else:
                dict[partstr] = flopcnt
                
    return dict

counts = assemble_dict(sys.argv[1])

print('IC Name\t\t\tcount\t(unused gates)')

cnt = 0
total_left = 0
for key in counts.keys():
    chip_cnt = int(key[key.find('_')+1:key.find('x')])
    n = ceil(counts[key] / chip_cnt)
    leftover = chip_cnt - counts[key] % chip_cnt

    # This seems to be necessary
    if counts[key] % chip_cnt == 0: 
        leftover = 0
    
    total_left += leftover
    cnt += n
    print(key, ':', n, '(' + str(leftover) + ')', sep='\t')

print('Total    ', ':', cnt, '(' + str(total_left) + ')', sep='\t')