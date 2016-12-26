#!/usr/bin/env python
import os
import sys
from Assembler import *

FILENAME = re.compile('([ \-\_\w]+).vm')


def path_to_string(path):
    asm = open(path)
    lines = ''
    for line in asm:
        lines += line
    asm.close()
    return lines


def getFilesInPath(path):
    files_list = os.listdir(arg[1])
    files = []
    for file in files_list:
        filename = os.path.join(path, file)
        if file.endswith('.vm') and os.path.isfile(filename):
            files.append(filename)
    return files


def argToPath(arg):
    if '.vm' in arg:
        arg = arg.replace('.vm', '')
        return arg + '.asm'
    if arg.rfind('\\') != -1:
        return os.path.join(arg, arg[arg.rfind('\\') + 1:] + '.asm')
    elif arg.rfind('/') != -1:
        return os.path.join(arg, arg[arg.rfind('/') + 1:] + '.asm')
    return arg + '.asm'


if __name__ == '__main__':
    arg = sys.argv
    path = argToPath(arg[1])
    if os.path.isdir(arg[1]):
        files = getFilesInPath(arg[1])
        writer = Writer(path)
    else:
        files = [arg[1]]
        writer = Writer(path)
    for asm_file in files:
        m = FILENAME.search(asm_file)
        FileParser(path_to_string(asm_file), m.group(1).replace(" ", "_"), writer)
    writer.save()
