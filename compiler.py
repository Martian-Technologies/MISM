import json
from codeSpliter import CodeSpliter

central_index = 0
def get_index():
    global central_index
    central_index += 1
    return central_index - 1

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd

Program = list[Command]

class Variable(object):
    def __init__(self, name: str):
        self.name = name

class Value(object):
    def __init__(self, value):
        self.value = value

class Comparator(object):
    def __init__(self, comparator: str):
        if comparator not in ['<', '>', '==', '!=', '<=', '>=']:
            raise Exception(f'comparator "{comparator}" is not a valid comparator')
        self.comparator = comparator

Instance = Variable | Value
Condition = tuple[Instance, Comparator, Instance]

class Nop(Command):
    def __init__(self):
        super().__init__('nop')

class Operator(object):
    def __init__(self, operator: str):
        if operator not in ['+', '-', '*', '/', '%', '^']:
            raise Exception(f'operator "{operator}" is not a valid operator')
        self.operator = operator


class DynamiclyAssignedVariable(Variable):
    def __init__(self, name: str, pointer_addr: int):
        super().__init__(name)
        self.pointer_addr = pointer_addr
        self.pointer_name = f'var_dyn_{name}_{get_index()}'

class StaticlyAssignedVariable(Variable):
    def __init__(self, name: str, addr: int):
        super().__init__(name)
        self.addr = addr
        self.pointer_name = f'var_dyn_{name}_{get_index()}'


class Function(Command):
    def __init__(self, name, inputs, code):
        super().__init__('func')
        self.name: str = name
        self.inputs: list[Variable] = inputs
        self.code: Program = code

class Branch(Command):
    def __init__(self, condition_code_pairs):
        super().__init__('branch')
        self.condition_code_pairs: dict[Condition, Program] = condition_code_pairs

class WhileLoop(Command):
    def __init__(self, condition: Condition, code: Program):
        super().__init__('while')
        self.init = Nop()
        self.condition: Condition = condition
        self.code: Program = code

class ForLoop(WhileLoop):
    def __init__(self, init: Command, condition: Condition, step: Command, code: Program):
        super().__init__(condition, code)
        self.init: Command = init
        self.code.append(step)

class Print(Command):
    def __init__(self, value: Instance):
        super().__init__('print')
        self.value: Instance = value

class Assignment(Command):
    def __init__(self, variable: Variable, value: Instance):
        super().__init__('assign')
        self.variable: Variable = variable
        self.value: Instance = value

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
        piecedCode = Compiler.piece(code)
        return piecedCode
        #return piecedCode

    @staticmethod
    def piece(parsedCode):
        i = 0
        piecedCode = []
        functions = []
        while i < len(parsedCode):
            codeLine = parsedCode[i]
            command = Compiler.make_command(codeLine)
            if command["type"] in ['else', 'elif']:
                if i > 0:
                    if piecedCode[i-1]["type"] in ['if', 'elif']:
                        piecedCode[i-1]['else'] = command
                    else:
                        raise Exception(f'{command.type} needs an if or elif statment before it')
                else:
                    raise Exception(f'{command.type} needs an if or elif statment before it')
            elif command["type"] == "function":
                functions.append(command)
            else:
                piecedCode.append(command)
            i += 1
        print(json.dumps(functions, indent=4))
        return piecedCode

    @staticmethod
    def make_command(line):
        command = {}
        if line[0] == 'for':
            if len(line) != 3:
                raise Exception(f"for statement {line} does not have: 'for', '(init, condition, increment)', 'code'")
            if len(line[1]) != 3:
                raise Exception(f"for statement {line} does not have: 'init', 'condition', 'increment'")
            command = {
                'type': 'for',
                'init': Compiler.make_command(line[1][0]),
                'condition': line[1][1],
                'increment': Compiler.make_command(line[1][2]),
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
            print(line)
            command = {
                'type': line[1],
                'var': line[0], # idk what to call this. TODO: help me name this
                'expression': line[2]
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