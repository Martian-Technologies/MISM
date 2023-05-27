import json
from codeSpliter import CodeSpliter
from codeTranslate import CodePiecer

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
        translatedCode = CodePiecer.piece(code)
        return translatedCode
        #return piecedCode

    @staticmethod
    def piece(parsedCode, functions = {}, functionName = None):
        i = 0
        piecedCode = []
        while i < len(parsedCode):
            codeLine = parsedCode[i]
            command = Compiler.make_command(codeLine, functions)
            if command["type"] in ['else', 'elif']:
                if len(piecedCode) > 0:
                    if piecedCode[len(piecedCode)-1]["type"] in ['if', 'elif']:
                        piecedCode[len(piecedCode)-1]['else'] = command
                    else:
                        raise Exception(f'{command.type} needs an if or elif statment before it')
                else:
                    raise Exception(f'{command.type} needs an if or elif statment before it')
            elif command["type"] == "function":
                if piecedCode[len(piecedCode)-1]['type'] == 'function setting':
                    if piecedCode[len(piecedCode)-1]['text'] == 'replace':
                        command['replace'] = True
                functions[command['name']] = command
            elif command["type"] == "return" and command['expression'] != None:
                if functionName == None:
                    raise Exception(f'return statments need to be in a function ')
                else:
                    functions[functionName]['return'] = True
            else:
                piecedCode.append(command)
            i += 1
        print("-----")
        print(json.dumps(functions, indent=4))
        return piecedCode

    @staticmethod
    def make_command(line, functions):
        command = {}
        if line[0] == 'for':
            if len(line) != 3:
                raise Exception(f"for statement {line} does not have: 'for', '(init, condition, increment)', 'code'")
            if len(line[1]) != 3:
                raise Exception(f"for statement {line} does not have: 'init', 'condition', 'increment'")
            command = {
                'type': 'for',
                'init': Compiler.make_command(line[1][0], functions),
                'condition': Compiler.make_condition(line[1][1], functions),
                'increment': Compiler.make_command(line[1][2], functions),
                'code': Compiler.piece(line[2])
            }
        elif line[0] == 'if':
            if len(line) != 3:
                raise Exception(f"if statement {line} does not have: 'if', 'condition', 'code'")
            command = {
                'type': 'if',
                'condition': Compiler.make_condition(line[1], functions),
                'code': Compiler.piece(line[2]),
                'else': None
            }
        elif line[0] == 'elif':
            if len(line) != 3:
                raise Exception(f"elif statement {line} does not have: 'elif', 'condition', 'code'")
            command = {
                'type': 'elif',
                'condition': Compiler.make_condition(line[1], functions),
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
                'condition': Compiler.make_condition(line[1], functions),
                'code': Compiler.piece(line[2])
            }
        elif line[0] == 'do':
            if len(line) != 4:
                raise Exception(f"do while loop {line} does not have: 'do', 'condition', 'code', 'while'")
            command = {
                'type': 'dowhile',
                'code': Compiler.piece(line[2]),
                'condition': Compiler.make_condition(line[2], functions)
            }
        elif line[0] == 'print':
            if len(line) != 2:
                raise Exception(f"print statement {line} does not have: 'print', 'expression'")
            command = {
                'type': 'print',
                'expression': Compiler.make_expression(line[1], functions)
            }
        elif line[0] == 'func':
            if len(line) != 4:
                raise Exception(f"function {line} does not have: 'func', 'name', ('args'), 'code'")
            command = {
                'type': 'function',
                'name': line[1],
                'replace': False,
                'params': line[2],
                'code': Compiler.piece(line[3], functions, line[1])
            }
        elif line[0] == 'return':
            if len(line) == 1:
                command = {
                    'type': 'return',
                    'expression': None
                }
            else:
                if len(line) != 2:
                    raise Exception(f"function {line} does not have: 'return', ('expression')")
                command = {
                    'type': 'return',
                    'expression': Compiler.make_expression(line[1], functions)
                }
        elif line[0][:1] == '@':
            command = {
                'type': 'function setting',
                'text': line[0][1:]
            }
        elif len(line) > 1:
            if line[1] in ['=', '+=', '-=', '*=', '/=']:
                if len(line) != 3:
                    raise Exception(f"statement {line} does not have: 'var', 'operator', 'expression'")
                command = {
                    'type': line[1],
                    'var': line[0], # idk what to call this. TODO: help me name this
                    'expression': Compiler.make_expression(line[2], functions)
                }
            elif line[1] in ['++', '--']:
                if len(line) != 2:
                    raise Exception(f"statement {line} does not have: 'var', 'operator'")
                command = {
                    'type': line[1],
                    'var': line[0], # idk what to call this. TODO: help me name this
                }
            elif line[0] in functions:
                if len(line) != 2:
                    raise Exception(f"statement {line} is wrongly called")
                if len(line[1]) != len(functions[line[0]]['params']):
                    raise Exception(f"statement {line} is does not have the params {functions[line[0]]['params']}")
                command = {
                    'type': "function call",
                    'name': line[0],
                    'args': Compiler.make_args(line[1], functions),
                }
            else:
                raise Exception(f"could not find command {line}")
        elif line[0] in functions:
            if len(line) != 2:
                raise Exception(f"statement {line} is wrongly called")
            if len(line[1]) != len(functions[line[0]]['params']):
                raise Exception(f"statement {line} is does not have the params {functions[line[0]]['params']}")
            command = {
                'type': "function call",
                'name': line[0],
                'args': Compiler.make_args(line[1], functions),
            }
        else:
            raise Exception(f"could not find command {line}")
        return command
    
    @staticmethod
    def make_args(args, functions):
        newArgs = []
        for expression in args:
            newArgs.append(Compiler.make_expression(expression, functions))
        return newArgs

    @staticmethod
    def make_expression(expression, functions):
        #added code to do this
        return {
            'type': 'expression',
            'expression': expression
            }
    
    def make_condition(expression, functions):
        if len(expression) == 0:
            raise Exception("can not leave condition blank")
        while len(expression) == 1 and type(expression[0]) == list:
            expression = expression[0]
        expressionSide1 = []
        expressionSide2 = []
        comparator = None
        for i in expression:
            if i in ['<', '>', '==', '!=', '<=', '>=']:
                comparator = i
            elif comparator == None:
                expressionSide1.append(i)
            else:
                expressionSide2.append(i)    
        if comparator == None:
            return {
                'type': 'non regular condition',
                'condition': expression
            }
        else:
            return {
                'type': 'condition',
                'comparator': comparator,
                'expressionLeft': Compiler.make_expression(expressionSide1, functions),
                'expressionRight': Compiler.make_expression(expressionSide2, functions)
            }