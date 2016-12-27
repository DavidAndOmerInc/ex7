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

    def goto(self, labelName):
        self.lines.append('@%s\n0;JMP\n' % labelName)
        # print('going to %s'%labelName)

    def ifgoto(self, labelName):
        print('if-> goto %s' % labelName)

    def addLabel(self, labelName):
        self.lines.append('(%s)\n' % labelName)
        # print('adding label %s'%labelName)

    def funcCall(self, title, funcName, nArgs):
        print('calling func %s %s %s' % (title, funcName, nArgs))

    def newFunction(self, title, funcName, nArgs):
        print('adding new function %s %s %s' % (title, funcName, nArgs))

    def doReturn(self):
        print('return')

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
ARITHACTION = re.compile('(add|sub|neg|and|or|eq|gt|lt|not)')
GOTOACTION = re.compile('(goto|label)')
PUSH = re.compile('push')
FIRSTGROUP = re.compile('(local|argument|temp|this|that)\s+([0-9]+)')
SECONDGROUP = re.compile('(constant|static)\s+([0-9]+)')
POINTER = re.compile('pointer\s+([0-1])')
LABEL = re.compile('label\s+([A-Za-z0-9\.\_\-]+)')
GOTO = re.compile('(if-goto|goto)\s+([A-Za-z0-9\.\_\-]+)')
isComment = re.compile("(\s*\/\/)")
RETURN = re.compile('return')
CALL = re.compile('(function|call)\s+([A-Za-z0-9\.\_\-]+)\s+(\d+)')


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
            m2 = ARITHACTION.search(line)
            m3 = GOTOACTION.search(line)
            if m:
                self.parseStack(line)
            elif m2:
                self.parseArtih(line)
            elif m3:
                self.parseGoto(line)
            else:
                self.parseFunc(line)

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

    def parseGoto(self, line):
        isLabel = LABEL.search(line)  ## getting group(1) == label
        goto = GOTO.search(line)  ## getting group(1) goto type, group(2) label name.
        if (isLabel):
            self.write.addLabel(isLabel.group(1))
            return
        elif goto.group(1) == 'goto':
            self.write.goto(goto.group(2))  # goto label name
        elif goto.group(1) == 'if-goto':
            self.write.ifgoto(goto.group(2))  # if than go to label name

    def parseFunc(self, line):
        # function funcName nArgs
        # call funcName nArgs
        # return
        # RETURN = re.compile('return')
        # CALL = re.compile('(function|call)\s+([A-Za-z0-9\.\_\-]+)\s+(\d+)')
        isReturn = RETURN.search(line)  # no grouping...
        if (isReturn):
            self.write.doReturn()
            return
        call = CALL.search(line)  ## group 1 = function \ call
        ## group 2 = function name
        ## group 3 = nArgs
        if call.group(1) == 'function':
            self.write.newFunction(self.title, call.group(2), call.group(3))
        elif call.group(1) == 'call':
            self.write.funcCall(self.title, call.group(2), call.group(3))
