# -*- coding: utf-8 -*-
import json
import os
import sys
from PIL import Image
import alpha_bmp

TJSDIR = ""
BMPDIR = ""
TJSBASE = ""

# DRACU-RIOT! cg 合并
# 1、使用 EMoteDumperXmoe.exe 解出 pimg 的 psb 文件后得到 XXX.psb.tjs 和 XXX 文件夹
# 2、执行 "yuzu-dracu-riot!-ev-merge.py XXX.psb.tjs" 进行合并

def getCommonPrefix(s1, s2):
    length = 1
    while length < len(s1) and s1[:length] == s2[:length]:
        length = length + 1
    return length - 1

def findBaseOfDiff(baseGroup, diff):
    for b in baseGroup:
        if getCommonPrefix(b['name'], diff['name']) > 0:
            return b
    return None

def main():
    tjs_name = sys.argv[1]

    global TJSDIR
    global BMPDIR
    global TJSBASE
    (TJSDIR,tempfilename) = os.path.split(tjs_name)
    TJSBASE = tempfilename[:tempfilename.find('.')]
    BMPDIR = os.path.join(TJSDIR, TJSBASE)

    json_name = BMPDIR + '.json'

    f = open(tjs_name, 'r')
    f.seek(0, 2)
    file_len = f.tell()
    f.seek(0, 0)
    data = f.read(file_len)
    data = data.replace('=>', ':').replace('(const)', '')
    content = list(data)
    data_len = len(data)

    idx_l = 0
    idx_r = data_len
    while True:
        res_l = data.find('[', idx_l)
        res_r = data.rfind(']', 0, idx_r)
        if res_l == -1 or res_r == -1:
            break

        if data[res_l-1] == '%':
            content[res_l-1] = ' '
            content[res_l] = '{'
            content[res_r] = '}'
        idx_l = res_l + 1
        idx_r = res_r - 1

        if idx_l >= data_len or idx_r >= data_len:
            break


    f2 = open(json_name, 'w')
    f2.write(''.join(content))
    f2.close()
    j = json.loads(''.join(content))

    # find base
    baseJsons = []
    if j['layers'][-1]['height'] == j['height'] and j['layers'][-1]['width'] == j['width']:
        baseJsons.append(j['layers'][-1])
    else:
        for item in j['layers']:
            if item['height'] == j['height'] and item['width'] == j['width']: # 搜索宽高一致
                baseJsons.append(item)

    if len(baseJsons) != 1:
        print("baseJsons size: ", len(baseJsons))
        return

    for item in j['layers']:
        baseItem = baseJsons[0]
        diff = alpha_bmp.BmpAlphaImageFile(os.path.join(BMPDIR, str(item['layer_id']) + '.bmp'))
        base = alpha_bmp.BmpAlphaImageFile(os.path.join(BMPDIR, str(baseItem['layer_id']) + '.bmp'))
        merge = Image.new('RGBA', (baseItem['width'], baseItem['height']))
        merge.paste(base, (0, 0, int(baseItem['width']), int(baseItem['height'])))
        left = item['left']
        top = item['top']
        right = left + diff.size[0]
        bottom = top + diff.size[1]
        merge.paste(diff, (left, top, right, bottom), diff)
        merge.save(os.path.join(BMPDIR, TJSBASE + '_merge_' + '{0:05}'.format(item['layer_id']) + '.png'), quality = 100)

if __name__ == '__main__':
    main()





