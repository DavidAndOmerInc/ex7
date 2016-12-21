#!/usr/bin/env python
import os
import sys
from Assembler import *

FILENAME = re.compile('([_a-zA-Z0-9]+).vm')


def path_to_string(path):
    # print('parsing : %s' % path)
    asm = open(path)
    lines = ''
    for line in asm:
        lines += line
    asm.close()
    return lines


if __name__ == '__main__':
    arg = sys.argv
    if os.path.isdir(arg[1]):
        if not arg[1].endswith('/'):
            arg[1] += '/'
        files = list()
        files_list = os.listdir(arg[1])
        for file in files_list:
            filename = arg[1] + file
            if file.endswith('.vm') and os.path.isfile(filename):
                files.append(filename)
        folder_path = arg[1][arg[1].rfind('/', 0, len(arg[1]) - 1) + 1:]
        folder_path = folder_path[:-1]
        writer = Writer(arg[1] + folder_path + '.asm')
        fn = folder_path[folder_path.rfind('\\') + 1:] # handling fn
        path = folder_path + '\\' + fn + '.asm'
    else:
        files = [arg[1]]
        path = arg[1][:arg[1].rfind('.')]+'asm'
    writer = Writer(os.path.join('',path))
    print(path)
    for asm_file in files:
        m = FILENAME.search(asm_file)
        FileParser(path_to_string(asm_file), m.group(1), writer)
    writer.save()

