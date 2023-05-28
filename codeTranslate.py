central_index = 0
def get_index():
    global central_index
    central_index += 1
    return central_index - 1

class NamespaceLayer(object):
    def __init__(self, name: str):
        self.name = name
        self.variables = []

class Namespace(object):
    def __init__(self):
        self.layers = [
            NamespaceLayer('root')
        ]
    
    def copy(self):
        new = Namespace()
        new.layers = self.layers.copy()
        return new
    
    def add_layer(self, name: str):
        self.layers.append(NamespaceLayer(name))
        return self
    
    def pop_layer(self):
        self.layers.pop()
        return self

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
    
    def __str__(self):
        return self.cmd
    
    def translate(self, namespace: Namespace):
        return []

Program = list[Command]

class Variable(object):
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self):
        return self.name

class Value(object):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)

class Comparator(object):
    def __init__(self, comparator: str):
        if comparator not in ['<', '>', '==', '!=', '<=', '>=']:
            raise Exception(f'comparator "{comparator}" is not a valid comparator')
        self.comparator = comparator
    
    def __str__(self):
        return self.comparator

Instance = Variable | Value
Condition = tuple[Instance, Comparator, Instance]

class Nop(Command):
    def __init__(self):
        super().__init__('nop')
    
    def translate(self, namespace: Namespace):
        return []

class Operator(object):
    def __init__(self, operator: str):
        if operator not in ['+', '-', '*', '/', '%', '^']:
            raise Exception(f'operator "{operator}" is not a valid operator')
        self.operator = operator
    
    def __str__(self):
        return self.operator


class DynamiclyAssignedVariable(Variable):
    def __init__(self, name: str, pointer_addr: int):
        super().__init__(name)
        self.pointer_addr = pointer_addr
        self.pointer_name = f'var_dyn_{name}_{get_index()}'
    
    def __str__(self):
        return print(f'<DynamiclyAssignedVariable name={self.name} pointer_addr={self.pointer_addr} pointer_name={self.pointer_name}>')

class StaticlyAssignedVariable(Variable):
    def __init__(self, name: str, addr: int):
        super().__init__(name)
        self.addr = addr
        self.pointer_name = f'var_dyn_{name}_{get_index()}'
    
    def __str__(self):
        return print(f'<StaticlyAssignedVariable name={self.name} addr={self.addr} pointer_name={self.pointer_name}>')


class Function(object):
    def __init__(self, name, inputs, code):
        self.name: str = name
        self.inputs: list[Variable] = inputs
        self.code: Program = code
    
    def __str__(self):
        return f'<Function name={self.name} inputs={self.inputs} code=\n{self.code}\n>'
    

class Branch(Command):
    def __init__(self, condition_code_pairs):
        super().__init__('branch')
        self.condition_code_pairs: dict[Condition, Program] = condition_code_pairs
    
    def __str__(self):
        return f'<Branch condition_code_pairs={self.condition_code_pairs}>'

class WhileLoop(Command):
    def __init__(self, condition: Condition, code: Program):
        super().__init__('while')
        self.init = Nop()
        self.condition: Condition = condition
        self.code: Program = code

    def __str__(self):
        return f'<WhileLoop condition={self.condition} code=\n{self.code}\n>'
    
    def translate(self, namespace: Namespace):
        self.break_jump = f'while_break_{get_index()}'
        self.start_jump = f'while_start_{get_index()}'
        out = []
        out += self.init.translate(namespace)
        out.append(f'JMIF {self.condition.translate(namespace)} ~{self.start_jump}')
        out.append(f'JUMP ~{self.break_jump}')
        out.append(f'{self.start_jump}:')
        out += [i.translate(namespace) for i in self.code]
        out.append(f'JUMP ~{self.start_jump}')
        out.append(f'{self.break_jump}:')
        return out

class ForLoop(WhileLoop):
    def __init__(self, init: Command, condition: Condition, step: Command, code: Program):
        super().__init__(condition, code)
        self.init: Command = init
        self.code.append(step)
    
    def __str__(self):
        return f'<ForLoop init={self.init} condition={self.condition} code=\n{self.code}\n>'

class Print(Command):
    def __init__(self, value: Instance):
        super().__init__('print')
        self.value: Instance = value
    
    def __str__(self):
        return f'<Print value={self.value}>'

class Assignment(Command):
    def __init__(self, variable: Variable, value: Instance):
        super().__init__('assign')
        self.variable: Variable = variable
        self.value: Instance = value
    
    def __str__(self):
        return f'<Assignment variable={self.variable} value={self.value}>'

class Modification(Command):
    def __init__(self, variable: Variable, operator: Operator, value: Instance):
        super().__init__('modify')
        self.variable: Variable = variable
        self.operator: Operator = operator
        self.value: Instance = value
    
    def __str__(self):
        return f'<Modification variable={self.variable} operator={self.operator} value={self.value}>'

class Definition(Command):
    def __init__(self, variable: Variable, value: Instance):
        super().__init__('define')
        self.variable: Variable = variable
        self.value: Instance = value
    
    def __str__(self):
        return f'<Definition variable={self.variable} value={self.value}>'

class Return(Command):
    def __init__(self, value: Instance):
        super().__init__('return')
        self.value: Instance = value
    
    def __str__(self):
        return f'<Return value={self.value}>'

class Continue(Command):
    def __init__(self):
        super().__init__('continue')

class Break(Command):
    def __init__(self):
        super().__init__('break')

class FunctionCall(Command):
    def __init__(self, name: str, inputs: list[Instance]):
        super().__init__('call')
        self.name: str = name
        self.inputs: list[Instance] = inputs
    
    def __str__(self):
        return f'<FunctionCall name={self.name} inputs={self.inputs}>'

class CodePiecer:
    @staticmethod
    def piece(code: list[object], namespace: Namespace=None):
        out = []
        if namespace is None:
            namespace = Namespace()
        for line in code:
            out.append(CodePiecer.make_command(line, namespace))
        return out

    @staticmethod
    def make_command(line, namespace: Namespace):
        command = {}
        if line[0] == 'for':
            if len(line) != 3:
                raise Exception(f"for statement {line} does not have: 'for', '(init, condition, increment)', 'code'")
            if len(line[1]) != 3:
                raise Exception(f"for statement {line} does not have: 'init', 'condition', 'increment'")
            command = {
                'type': 'for',
                'init': CodePiecer.make_command(line[1][0], namespace),
                'condition': line[1][1],
                'increment': CodePiecer.make_command(line[1][2], namespace),
                'code': CodePiecer.piece(line[2], namespace)
            }
        elif line[0] == 'if':
            if len(line) != 3:
                raise Exception(f"if statement {line} does not have: 'if', 'condition', 'code'")
            command = {
                'type': 'if',
                'condition': line[1],
                'code': CodePiecer.piece(line[2]),
                'else': None
            }
        elif line[0] == 'elif':
            if len(line) != 3:
                raise Exception(f"elif statement {line} does not have: 'elif', 'condition', 'code'")
            command = {
                'type': 'elif',
                'condition': line[1],
                'code': CodePiecer.piece(line[2]),
                'else': None
            }
        elif line[0] == 'else':
            if len(line) != 2:
                raise Exception(f"else statement {line} does not have: 'else', 'code'")
            command = {
                'type': 'else',
                'code': CodePiecer.piece(line[1]),
            }
        elif line[0] == 'while':
            if len(line) != 3:
                raise Exception(f"while loop {line} does not have: 'while', 'condition', 'code'")
            command = {
                'type': 'while',
                'condition': line[1],
                'code': CodePiecer.piece(line[2])
            }
        elif line[0] == 'do':
            if len(line) != 4:
                raise Exception(f"do while loop {line} does not have: 'do', 'condition', 'code', 'while'")
            command = {
                'type': 'dowhile',
                'code': CodePiecer.piece(line[2]),
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
            code = CodePiecer.piece(line[3], namespace.copy().add_layer(line[1]))
            command = Function(line[1], line[2], code)
        elif line[1] in ['=', '+=', '-=', '*=', '/=', ':=']:
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
            command = str(Modification(line[0], line[1][0], Value(1)))
        else:
            raise Exception(f"could not find command {line}")
        return command