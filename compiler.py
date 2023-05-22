from codeSpliter import CodeSpliter

class Compiler:
    """used to compile code into assembly code"""

    reserved = {
        'if': 'IF',
        'then': 'THEN',
        'else': 'ELSE',
        'while': 'WHILE',
        'do': 'DO',
        'end': 'END',
        'print': 'PRINT',
        'for': 'FOR'
    }

    """
    Please use functions to make code easier to read.
    You have a horibal habit to make all the code in one giant block.
    Please make helper functions. You should have a ton, you have one.
    """

    @staticmethod
    def compile(inputCode):
        """
        Compiles code into assembly.\n
        Input a string containing all the code that you want to compile.
        """
        code = CodeSpliter.split(inputCode)
        print(code)
        piecedCode = Compiler.piece(code)
        print(piecedCode)
        return piecedCode
        #return piecedCode

    @staticmethod
    def piece(parsedCode):
        i = 0
        piecedCode = []
        while i < len(parsedCode):
            codeLine = parsedCode[i]
            command = Compiler.makeCommand(codeLine)
            if command["type"] in ['else', 'elif']:
                if i > 0:
                    if piecedCode[i-1]["type"] in ['if', 'elif']:
                        piecedCode[i-1]['else'] = command
                    else:
                        raise Exception(f'{command.type} needs an if or elif statment before it')
                else:
                    raise Exception(f'{command.type} needs an if or elif statment before it')
            else:
                piecedCode.append(command)
            i += 1
        return piecedCode

    @staticmethod
    def makeCommand(line):
        command = {}
        print(line)
        if line[0] == 'for':
            if len(line) != 3:
                raise Exception(f"for statement {line} does not have: 'for', '(init, condition, increment)', 'code'")
            if len(line[1]) != 3:
                raise Exception(f"for statement {line} does not have: 'init', 'condition', 'increment'")
            command = {
                'type': 'for',
                'init': Compiler.makeCommand(line[1][0]),
                'condition': line[1][1],
                'increment': Compiler.makeCommand(line[1][2]),
                'code': Compiler.piece(line[2])
            }
        elif line[0] == 'if':
            if len(line) != 3:
                raise Exception(f"if statement {line} does not have: 'if', 'condition', 'code'")
            command = {
                'type': 'if',
                'condition': line[1],
                'code': Compiler.piece(line[2]),
                'else': None
            }
        elif line[0] == 'elif':
            if len(line) != 3:
                raise Exception(f"elif statement {line} does not have: 'elif', 'condition', 'code'")
            command = {
                'type': 'elif',
                'condition': line[1],
                'code': Compiler.piece(line[2]),
                'else': None
            }
        elif line[0] == 'else':
            if len(line) != 2:
                raise Exception(f"else statement {line} does not have: 'else', 'code'")
            command = {
                'type': 'else',
                'code': Compiler.piece(line[1]),
            }
        elif line[0] == 'while':
            if len(line) != 3:
                raise Exception(f"while loop {line} does not have: 'while', 'condition', 'code'")
            command = {
                'type': 'while',
                'condition': line[1],
                'code': Compiler.piece(line[2])
            }
        elif line[0] == 'do':
            if len(line) != 4:
                raise Exception(f"do while loop {line} does not have: 'do', 'condition', 'code', 'while'")
            command = {
                'type': 'dowhile',
                'code': Compiler.piece(line[2]),
                'condition': line[2]
            }
        elif line[0] == 'print':
            if len(line) != 2:
                raise Exception(f"print statement {line} does not have: 'print', 'expression'")
            command = {
                'type': 'print',
                'expression': line[1]
            }
        elif line[0] == 'func':
            if len(line) != 4:
                raise Exception(f"function {line} does not have: 'func', 'name', 'args', 'code'")
            command = {
                'type': 'function',
                'name': line[1],
                'args': line[2],
                'code': Compiler.piece(line[3])
            }
        elif line[1] in ['=', '+=', '-=', '*=', '/=']:
            if len(line) != 3:
                raise Exception(f"statement {line} does not have: 'var', 'operator', 'expression'")
            command = {
                'type': line[1],
                'var': line[0], # idk what to call this. TODO: help me name this
                'expression': line[2:]
            }
        elif line[1] in ['++', '--']:
            if len(line) != 2:
                raise Exception(f"statement {line} does not have: 'var', 'operator'")
            command = {
                'type': line[1],
                'var': line[0], # idk what to call this. TODO: help me name this
            }
        else:
            raise Exception(f"could not find command {line}")
        return command