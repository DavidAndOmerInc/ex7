import re
from arithmeticStrings import Arith


class Writer:
    GROUP = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}

    def __init__(self, path):
        self.path = path
        self.lines = []

    def push_second_group(self, i):  # used for constant and static
        self.lines.append('\n@%s\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1' % i)

    def push_staticVar(self, i):  # used for constant and static
        self.lines.append('\n@%s\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1' % i)

    def pop_second_group(self, i):
        self.lines.append('\n@SP\nM=M-1\nA=M\nD=M\n@%s\nM=D' % i)

    def pop_first_group(self, i, group):  # fits for local, this, that, argument
        if group == 'temp':
            self.lines.append('\n@%s\nD=A\n@5\nD=A+D\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@13\nA=M\nM=D\n' % i)
            return
        self.lines.append(
            '@%s\nD=A\n@%s\nD=D+M\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R13\nA=M\nM=D\n' % (i, self.GROUP[group]))

    def push_first_group(self, i, group):  # fits for local, this, that, argument,
        if group == 'temp':
            self.lines.append('@%s\nD=A\n@5\nA=D+A\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n' % i)
            return
        self.lines.append('@%s\nD=A\n@%s\nA=D+M\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n' % (i, self.GROUP[group]))

    def pushPointer(self, num):
        if num == '0':
            state = 'THIS'
        else:
            state = 'THAT'
        self.lines.append('@%s\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n' % state)

    def popPointer(self, num):
        if num == '0':
            state = 'THIS'
        else:
            state = 'THAT'
        self.lines.append('@SP\nA=M-1\nD=M\n@SP\nM=M-1\n@%s\nM=D\n' % state)

    def writeArith(self, state):
        self.lines.append(state.replace(' ', ''))

    def save(self):
        with open(self.path, 'w') as file:
            for line in self.lines:
                line = line.split('\n')
                for elem in line:
                    if elem == '':
                        continue
                    file.write(elem)
                    file.write('\n')


'''
blocks!
0-15 virtual registers
16-255 static variables
2048-16483 heap
16384-24575 memory mapped I/O

registers
ram[0] SP stack pointer
ram[1] LCL points to the current VM function
ram[2] ARG points the current function`s argument var
ram[3] THIS points to current this (in the heap)
ram[4] THAT points to current that (heap 2)
ram[5-12] hold conents of temp
ram[13-15] general purposes registers.

local, argument, this, that :

'''

STACKACTION = re.compile('(pop|push)')
PUSH = re.compile('push')
FIRSTGROUP = re.compile('(local|argument|temp|this|that) ([0-9]+)')
SECONDGROUP = re.compile('(constant|static) ([0-9]+)')
POINTER = re.compile('pointer ([0-1])')
isComment = re.compile("(\s*\/\/)")


class FileParser:
    def __init__(self, content, title, writer):
        self.content = content
        self.title = title
        self.write = writer
        self.remove_comments()
        self.arith = Arith()
        self.parse_content()

    def remove_comments(self):
        lines = self.content.split("\n")
        parsed_lines = []
        for line in lines:
            m = isComment.search(line)
            if m:
                line = line[0:m.span()[0]]
            if line is '':
                continue
            parsed_lines.append(line)
        self.content = parsed_lines

    def parse_content(self):
        for line in self.content:
            m = STACKACTION.search(line)
            if m:
                self.parseStack(line)
            else:
                self.parseArtih(line)

    def parseStack(self, line):
        m = PUSH.search(line)
        if m:
            self.parsePush(line)
        else:
            self.parsePop(line)

    def parsePush(self, line):
        m1 = FIRSTGROUP.search(line)
        m2 = SECONDGROUP.search(line)
        m3 = POINTER.search(line)
        if m1:
            self.write.push_first_group(m1.group(2), m1.group(1))
        elif m2:
            if m2.group(1) == 'static':
                var = self.title + ".%s" % m2.group(2)
                self.write.push_staticVar(var)
            else:
                var = m2.group(2)
                self.write.push_second_group(var)
        elif m3:
            self.write.pushPointer(m3.group(1))

    def parsePop(self, line):
        m1 = FIRSTGROUP.search(line)
        m2 = SECONDGROUP.search(line)
        m3 = POINTER.search(line)
        if m1:
            # #print('translated %s ----> pull %s %s' % (line, m1.group(1), m1.group(2)))
            self.write.pop_first_group(m1.group(2), m1.group(1))
        elif m2:
            # print('translated %s ----> pull %s %s' % (line, m2.group(1), m2.group(2)))
            if m2.group(1) == 'static':
                i = self.title + ".%s" % m2.group(2)
            else:
                i = m2.group(1)
            self.write.pop_second_group(i)
        elif m3:
            # #print('translated %s ----> pull pointer %s' % (line, m3.group(1)))
            self.write.popPointer(m3.group(1))

    def parseArtih(self, line):
        # we should parse the following
        # easy : add, sub, neg
        # hard : eq, gt, lt, and, or , not
        line = line.replace(' ', '')
        self.di = {'add': self.arith.cmd_add, 'sub': self.arith.cmd_sub, 'neg': self.arith.cmd_neg,
                   'and': self.arith.cmd_and, 'or': self.arith.cmd_or, 'eq': self.arith.cmd_eq,
                   'gt': self.arith.cmd_gt, 'lt': self.arith.cmd_lt, 'not': self.arith.not_cmd}
        self.write.writeArith(self.di[line]())
