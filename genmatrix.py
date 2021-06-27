#!/usr/bin/python3

import sys
import getopt
from PIL import Image,ImageDraw,ImageFont

def mono_genmatrix(image, flip, scan_dir, endian, color_reverse):
    width = image.size[0]
    height = image.size[1]

    if flip == 'X':
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    elif flip == 'Y':
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

    if scan_dir == 'H':
        scan_direction = 'Horizontal'
    else:
        scan_direction = 'Vertical'

    if endian == 'B':
        byte_reverse = True
    else:
        byte_reverse = False

    if color_reverse == 'true':
        color_reverse = True
    else:
        color_reverse = False

    unalign = 0
    matrix = list()
    
    if scan_direction == 'Horizontal':
        if (width%8) != 0:
            unalign = 1
        for i in range(0, height):
            for j in range(0, (width//8)+unalign):
                v = 0x00
                rs = 8*j
                re = 8*(j+1)
                if re > width:
                    re = width
                for k in range(rs, re):
                    if image.getpixel((k, i)) != 0:
                        if not byte_reverse:
                            v |= (0x01 << (k%8))
                        else:
                            v |= (0x01 << (7-(k%8)))
                if color_reverse:
                    v ^= 0xff
                matrix.append(v)
    elif scan_direction == 'Vertical':
        if (height%8) != 0:
            unalign = 1
        for i in range(0, width):
            for j in range(0, (height//8)+unalign):
                v = 0x00
                rs = 8*j
                re = 8*(j+1)
                if re > height:
                    re = height
                for k in range(rs, re):
                    if image.getpixel((i, k)) != 0:
                        if not byte_reverse:
                            v |= (0x01 << k%8)
                        else:
                            v |= (0x01 << (7-k%8))
                if color_reverse:
                    v ^= 0xff
                matrix.append(v)
    return matrix

def show_matrix(matrix):
    i = 0
    for v in matrix:
        print('0x%02x, ' % v, end='')
        i += 1
        if i == 16:
            i = 0
            print()

def main():
    help = 'Usage: %s [option]' % sys.argv[0]
    help += '''\nOption:
    -h | --help                 显示帮助信息

    -O | --operation            要执行的操作，默认为str
                                str: 字符取模, mono: 单色图片取模

    -F | --flip                 图片翻转
                                X: 上下翻转, Y: 左右翻转

    -S | --scan-dir             扫描方向，默认为水平扫描
                                H:水平扫描, V:垂直扫描

    -E | --endian               字节序列选择，默认为小端序
                                L: 小端序，低地址像素点位于字节低位 pixel 0 -> bit0
                                B: 大端序，低地址像素点位于字节高位 pixel 0 -> bit7

    -H | --character-height     字符高度，默认为16，str操作下有效

    -R                          颜色反转，默认不反转
                                正常：白色: 1, 黑色: 0
                                反转: 白色: 0, 黑色: 1

Example:

    (1) 生成指定图片的像素矩阵 (水平扫描, 小端序, 颜色反转)
    ./genmatrix -O mono -R xxx.bmp

    (2) 生成字符串序列的像素矩阵 (16x16, 垂直扫描, 大端序, 颜色正常)
    ./genmatrix -O str -S V -E B '中华人民共和国'
'''
    short_opts = 'hO:F:S:E:H:R'
    opts = ['help', 'operation', 'flip' 'scan-dir', 'endian', 'character-height']

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, opts)
    except getopt.GetoptError as err:
        print(err)
        print(help)
        sys.exit(1)

    operation       = 'str'
    flip            = 'false'
    scan_dir        = 'H'
    endian          = 'L'
    char_height     = '16'
    color_reverse   = 'false'

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help)
            sys.exit()
        elif opt in ('-O', '--operation'):
            if arg not in ('str', 'mono'):
                print('不支持的参数: ' + opt + ' ' + arg)
                sys.exit(1)
            operation = arg
        elif opt in ('-F', '--flip'):
            if arg not in ('X', 'Y'):
                print('不支持的参数: ' + opt + ' ' + arg)
                sys.exit(1)
            flip = arg
        elif opt in ('-S', '--scan-dir'):
            if arg not in ('H', 'V'):
                print('不支持的参数: ' + opt + ' ' + arg)
                sys.exit(1)
            scan_dir = arg
        elif opt in ('-E', '--endian'):
            if arg not in ('L', 'B'):
                print('不支持的参数: ' + opt + ' ' + arg)
                sys.exit(1)
            endian = arg
        elif opt in ('-H', '--character-height'):
            char_height = arg
        elif opt in ('-R'):
            color_reverse = 'true'
        else:
            print(help)
            sys.exit(1)

    if len(args) > 0:
        arg = args[0]
    else:
        print('缺少目标文件或字符串')
        print(help)
        sys.exit(1)

    print('\n操作类型: ' + operation)
    if operation == 'str':
        print('字符高度: ' + char_height)
    print('图像翻转: ' + flip)
    print('扫描方向: ' + scan_dir)
    print('字节序列: ' + endian)
    print('颜色反转: ' + color_reverse + '\n')

    if operation == 'mono':
        img = Image.open(arg)
        matrix = mono_genmatrix(img, flip, scan_dir, endian, color_reverse)
        show_matrix(matrix)
        img.close()
    else:
        # 排序，方便目标设备使用二分法查找
        l = list(arg)
        l.sort()
        arg = ''.join(l)
        for s in arg:
            c = s.encode('utf-8')
            print('/* %c */' % s)
            if c[0] < 128:
                w = int(char_height)//2
                print('/* utf-8 code: %02x */' % c[0])
            else:
                w = int(char_height)
                print('/* utf-8 code: %02x%02x%02x */' % (c[0], c[1], c[2]))
            h = int(char_height)
            img = Image.new("1", (w,h), (1))
            ttfont = ImageFont.truetype("fonts/unifont-13.0.06.ttf", int(char_height))
            draw = ImageDraw.Draw(img)
            draw.text((0,0), u'%c' % s, (0), font=ttfont)
            matrix = mono_genmatrix(img, flip, scan_dir, endian, color_reverse)
            show_matrix(matrix)
            img.close()

if __name__ == '__main__':
    main()

