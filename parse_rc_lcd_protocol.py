import sys
#input_file = r'C:\Users\mouse\Desktop\init.bin'
input_file = sys.argv[1]
output_file = '{0}.txt'.format(input_file)

f = open(input_file, 'rb')


pre_cs = 1
pre_wr = 1

frame_start = False
word_start = False

bits_per_word = 13
words_per_frame = 16

frames = []
words = []
bits = []

sample_rate = 0
time = 0
last_word_time = -1

while True:
    b = f.read(1)
    if not b:
        break
    
    b = b[0]

    time = time + 1

    cs = b & 0x01
    wr = b & 0x02
    data = b & 0x04

    if not frame_start:
        if cs == 0:
            frame_start = True
            words = []
    else:
        if not word_start:
            if cs == 0:
                word_start = True
                last_word_time = -1
                bits = []

            if last_word_time > 0 and time - last_word_time > 250:
                frames.append(words)
                frame_start = False
        else:
            if pre_wr == 0 and wr != 0:
                if data == 0:
                    bits.append(0)
                else:
                    bits.append(1)
                if len(bits) > bits_per_word:
                    print('ERROR: frame[{0}]word[{1}]bits:{2}'.format(len(frames), len(words), len(bits)))

            if pre_cs == 0 and cs != 0:
                word_start = False
                words.append(bits)
                last_word_time = time

                #if len(words) > words_per_frame:
                #    print('ERROR: frame[{0}]word[{1}] '.format(len(frames), len(words)))

    pre_cs = cs
    pre_wr = wr

o = open(output_file, 'w')
n = 0
for frame in frames:
    o.write('{0}\t'.format(n))
    n = n + 1
    for word in frame:
        num = 0
        for bit in word:
            num = num*2 + bit
        o.write('0x{0:04X},'.format(num))
    
    o.write('\t')
    for word in frame:
        if word[0:4] != [1,0,1,1]:
            pass
        for bit in word:
            o.write(str(bit))
        o.write('\t')
    o.write('\n')


o.close()
f.close()