import re
from arithmeticStrings import Arith


class Writer:
    def __init__(self, path):
        self.path = path
        self.lines = []
        
    def pushSecondGroup(self,i):  ### used for constant and static
        self.lines.append('\n@%s\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'%i)

    def popSecondGroup(self,i):
        self.lines.append('@SP\nA=M\nD=M\n@SP\nM=M-1\n@%s\nM=D\n'%i)

    def popFirstGroup(self,i,group): # fits for local, this, that, argument
        if(group == 'temp'):
            self.lines.append('@SP\nA=M\nD=M\n@SP\nM=M-1\n@5\nA=A+%s\nM=D\n'%i)
            return
        self.lines.append('@SP\nA=M\nD=M\n@SP\nM=M-1\n@%s\nA=A+%s\nM=D\n'%(group,i))

    def pushFirstGroup(self,i,group): # fits for local, this, that, argument,
        if(group == 'temp'):
            self.lines.append('@5\nA=A+%s\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n' %i)
            return
        self.lines.append('@%s\nA=A+%s\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'%(group,i))

    def push_second_group(self, i):  # used for constant and static
        self.lines.append('\n@%s\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1' % i)

    def pop_second_group(self, i):
        self.lines.append('\n@SP\nA=M\nD=M\n@SP\nM=M-1\n@%s\nM=D' % i)

    def pop_first_group(self, i, group):  # fits for local, this, that, argument
        if group == 'temp':
            self.lines.append('\n@SP\nA=M\nD=M\n@SP\nM=M-1\n@5\nA=A+%s\nM=D\n' % i)
            return
        self.lines.append('\n@SP\nA=M\nD=M\n@SP\nM=M-1\n@%s\nA=A+%s\nM=D' % (group, i))

    def push_first_group(self, i, group):  # fits for local, this, that, argument,
        if group == 'temp':
            self.lines.append('\n@5\nA=A+%s\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1' % i)
            return
        self.lines.append('\n@%s\nA=A+%s\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1' % (group, i))


    def push_pointer(self, num):
        if num == '0':
            state = 'THIS'
        else:
            state = 'THAT'
        self.lines.append('@%s\nA=M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'%state)
        self.lines.append('\n@%s\nA=M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1' % state)


    def pop_pointer(self, num):
        if num == '0':
            state = 'THIS'
        else:
            state = 'THAT'
        self.lines.append('@SP\nA=M\nD=M\n@SP\nM=M-1\n@%s\nA=M\nM=D\n' % state)
    def writeArith(self,string):
        self.lines.append(string.replace(' ',''))
        self.lines.append('\n@SP\nA=M\nD=M\n@SP\nM=M-1\n@%s\nA=M\nM=D' % state)

    def write_arith(self, string):
        self.lines.append(string.replace(' ', ''))

    def save(self):
        with open(self.path, 'w') as file:
            for line in self.lines:
                line = line.split('\n')
                for elem in line:
                    if(elem == ''):
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

STACKACTION = re.compile('(pull|push)')
PUSH = re.compile('push')
FIRSTGROUP = re.compile('(local|argument|temp|this|that) ([0-9]+)')
SECONDGROUP = re.compile('(constant|static) ([0-9]+)')
POINTER = re.compile('pointer ([0-1])')
isComment = re.compile("[ ]*//")


class FileParser:
    def __init__(self, content, title, writer):
        self.content = content
        self.title = title
        self.write = writer
        self.remove_comments()
        self.arith = Arith()
        print(self.content)
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
            self.parsePull(line)

    def parsePush(self, line):
        m1 = FIRSTGROUP.search(line)
        m2 = SECONDGROUP.search(line)
        m3 = POINTER.search(line)
        if m1:
            print('translated %s ----> push %s %s' % (line, m1.group(1), m1.group(2)))
            self.write.push_first_group(m1.group(2), m1.group(1))
        elif m2:
            print('translated %s ----> push %s %s' % (line, m2.group(1), m2.group(2)))
            if m2.group(1) is 'static':
                i = self.title + ".%s" % m2.group(2)
            else:
                i = m2.group(2)
            self.write.push_second_group(i)
        elif m3:
            print('translated %s ----> push pointer %s' % (line, m3.group(1)))
            self.write.push_pointer(m2.group(1))

    def parsePull(self, line):
        m1 = FIRSTGROUP.search(line)
        m2 = SECONDGROUP.search(line)
        m3 = POINTER.search(line)
        if m1:
            print('translated %s ----> pull %s %s' % (line, m1.group(1), m1.group(2)))
            self.write.pullFirstGroup(m1.group(2), m1.group(1))
        elif m2:
            print('translated %s ----> pull %s %s' % (line, m2.group(1), m2.group(2)))
            if m2.group(1) is 'static':
                i = self.title + ".%s" % m2.group(1)
            else:
                i = m2.group(1)
            self.write.pullSecondGroup(i)
        elif m3:
            print('translated %s ----> pull pointer %s' % (line, m3.group(1)))
            self.write.pullPointer(m2.group(1))

    def parseArtih(self, line):
        # we should parse the following
        # easy : add, sub, neg
        # hard : eq, gt, lt, and, or , not
        line = line.replace(' ', '')
        self.di = {'add': self.arith.cmd_add, 'sub': self.arith.cmd_sub, 'neg': self.arith.cmd_neg,
                   'and': self.arith.cmd_and, 'or': self.arith.cmd_or, 'eq': self.arith.cmd_eq,
                   'gt': self.arith.cmd_gt, 'lt': self.arith.cmd_lt, 'not': self.arith.not_cmd}
        self.write.write_arith(self.di[line]())
