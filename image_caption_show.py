# 为格式转换而写的临时脚本，以后可以加到 bloom 的功能里面

import re
import sys

filename = sys.argv[1]

with open(filename, 'r') as f:
    for line in f:
        line = line.strip('\n')
        print(line)
        if line.startswith('!'):
            # image
            # greedy mode needed
            m = re.match(r'!\[(.*)\]\(.*\)', line)
            caption = m.group(1)
            if len(caption) > 0:
                print(f'（{caption}）')
