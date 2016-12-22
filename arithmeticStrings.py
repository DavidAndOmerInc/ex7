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
            M = M - 1
            A = M
            D = M
            A = A - 1
            D = D - M
            @NEQ.%s
            D;JNE
            @SP
            A = M - 1
            M = -1
            @END.%s
            0;JMP
            (NEQ.%s)
            @SP
            A = M - 1
            M = 0
            (END.%s)
            """.replace('%s', self.generateID())

    def cmd_gt(self):
        return """@SP
            M = M - 1
            A = M - 1
            D = M
            @A_LE.%s
            D;JLE
            @SP
            A = M
            D = M
            @GT.%s
            D;JLT
            @SP
            A = M - 1
            D = M - D
            @GT.%s
            D;JGT
            @N_GT.%s
            0;JMP
            (A_LE.%s)
            @SP
            A = M
            D = M
            @N_GT.%s
            D;JGT
            @SP
            A = M - 1
            D = M - D
            @GT.%s
            D;JGT
            @N_GT.%s
            0;JMP
            (GT.%s)
            @SP
            A = M - 1
            M = -1
            @END.%s
            0;JMP
            (N_GT.%s)
            @SP
            A = M - 1
            M = 0
            (END.%s)
            """.replace('%s', self.generateID())

    def cmd_lt(self):
        return '''@SP
            M = M - 1
            A = M - 1
            D = M
            @A_LE.%s
            D;JLE
            @SP
            A = M
            D = M
            @N_LT.%s
            D;JLE
            @SP
            A = M - 1
            D = M - D
            @LT.%s
            D;JLT
            @N_LT.%s
            0;JMP
            (A_LE.%s)
            @SP
            A = M
            D = M
            @LT.%s
            D;JGT
            @SP
            A = M - 1
            D = M - D
            @LT.%s
            D;JLT
            @N_LT.%s
            0;JMP
            (LT.%s)
            @SP
            A = M - 1
            M = -1
            @END.%s
            0;JMP
            (N_LT.%s)
            @SP
            A = M - 1
            M = 0
            (END.%s)
            '''.replace('%s', self.generateID())

    def not_cmd(self):
        return """@SP
            A = M-1
            M = !M
            """

# we should parse the following
# easy : add, sub, neg
# hard : eq, gt, lt, and, or , not
