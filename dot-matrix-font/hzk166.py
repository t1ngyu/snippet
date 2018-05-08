

def draw(shape):
    result = []
    for idx, byte in enumerate(shape):
        for bit_idx in range(7, -1, -1):
            if (byte >> bit_idx) & 0x01:
                result.append('*')
            else:
                result.append('.')
        if idx % 2:
            result.append('\n')
    return ''.join(result)


def draw_char(char, fontdata):
    '''
    hzk16内偏移地址计算方法：
        字符的GBK编码为（2字节）AB
        offset = [(A-0xA1)*94 + (B-0xA1)] * 32
    '''
    data = char.encode('gbk')
    offset = ((data[0] - 0xA1) * 94 + (data[1] - 0xA1)) * 32
    return draw(fontdata[offset: offset + 32])

def draw_str(text, fontdata):
    for char in text:
        print(draw_char(char, fontdata))

def main():

    fontdata = open('HZK16', 'rb').read()

    draw_str('你好！', fontdata)


main()