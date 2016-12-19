id = 0


class Arith:
    def __init__(self):
        return

    def generateID(self):
        global id
        id += 1
        return str(id)

    def cmd_add(self):
        return """@SP
            M=M-1
            A=M
            D=M
            @SP
            A=M-1
            M=D+M
        """

    def cmd_sub(self):
        return """@SP
            M=M-1
            A=M
            D=M
            @SP
            A=M-1
            M=M-D
          """

    def cmd_neg(self):
        return """@0
              D=A
              @SP
              A=M-1
              M=D-M
            """

    def cmd_and(self):
        return """@SP
                M = M-1
                A = M
                D = M
                @SP
                M = M-1
                A = M
                M = D&M
                @SP
                M = M+1
              """

    def cmd_or(self):
        return """@SP
            M = M-1
            A = M
            D = M
            @SP
            M = M-1
            A = M
            M = D|M
            @SP
            M = M+1
            """

    def cmd_eq(self):
        return """@SP
            A=M-1
            D=M
            D=-D
            @SP
            M=M-1
            A=M-1
            D=D+M
            @TRUE.%s
            D;JEQ
            @FALSE.%s
            0;JMP
            (TRUE.%s)
            @0
            D = A-1
            @END.%s
            0;JMP
            (FALSE.%s)
            @0
            D = A
            (END.%s)
            @SP
            A = M-1
            M = D
            """.replace('%s', self.generateID())
    def cmd_gt(self):
        return """@SP
            A=M-1
            D=M
            D=-D
            @SP
            M=M-1
            A=M-1
            D=D+M
            @TRUE.%s
            D;JGT
            @FALSE.%s
            0;JMP
            (TRUE.%s)
            @0
            D = A-1
            @END.%s
            0;JMP
            (FALSE.%s)
            @0
            D = A
            (END.%s)
            @SP
            A = M-1
            M = D
            """.replace('%s', self.generateID())

    def cmd_lt(self):
        return '''@SP
            A=M-1
            D=M
            D=-D
            @SP
            M=M-1
            A=M-1
            D=D+M
            @TRUE.%s
            D;JLT
            @FALSE.%s
            0;JMP
            (TRUE.%s)
            @0
            D = A-1
            @END.%s
            0;JMP
            (FALSE.%s)
            @0
            D = A
            (END.%s)
            @SP
            A = M-1
            M = D
            '''.replace('%s', self.generateID())

    def not_cmd(self):
        return """@SP
            A = M-1
            M = !M
            """

# we should parse the following
# easy : add, sub, neg
# hard : eq, gt, lt, and, or , not
