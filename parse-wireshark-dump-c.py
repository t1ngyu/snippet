import re

def parse_data(filename):
    with open(filename, 'r') as fp:
        lines = fp.readlines()
    groups = []
    for line in lines:
        if line.startswith('char'):
            peer = int(re.search(r'peer(\d+)', line).group(1))
            # print(f'{peer}: {line}')
            groups.append((peer, bytearray()))
        elif line.startswith('0x'):
            # print(f'{line}')
            data = bytes.fromhex(line.strip(' \r\n};').replace('0x', '').replace(',', '').replace(' ', ''))
            groups[-1][1].extend(data)
    return groups