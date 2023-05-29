import copy
import json
from expressionMaker import ExpressionMaker
from varNameGen import VariableNameGenerator

if __name__ == "__main__":
    import main

class Piecer:
    @staticmethod
    def piece(parsedCode, outsideFunctions = {}, functionNames = []):
        functions = {}
        i = 0
        piecedCode = []
        while i < len(parsedCode):
            codeLine = parsedCode[i]
            command = Piecer.make_command(codeLine, outsideFunctions.copy() | functions.copy(), functionNames)
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
                del piecedCode[len(piecedCode)-1]
                functions[command['name']] = command
            elif command["type"] == "return":
                if len(functionNames) == 0:
                    raise Exception(f'return statment {command} needs to be in a function')
                if outsideFunctions[functionNames[0]]['return'] == None:
                    outsideFunctions[functionNames[0]]['return'] = (command['expression'] != None)
                elif outsideFunctions[functionNames[0]]['return'] == (command['expression'] == None):
                    raise Exception(f'return statments for function {functionNames[0]} needs to all return or not return a value')
                
                if outsideFunctions[functionNames[0]]['return']:
                    piecedCode.insert(0, {'type': 'define', 'var': VariableNameGenerator.get_return_name(functionNames[0])})
                    piecedCode.append({'type': '=', 'var': VariableNameGenerator.get_return_name(functionNames[0]), 'expression': command['expression']})
            else:
                piecedCode.append(command)
            i += 1
        piecedCode = Piecer.replace_functions(piecedCode, outsideFunctions.copy() | functions.copy())
        for name in list(functions.keys()).copy():
            if functions[name]['replace']:
                del functions[name]
        return ExpressionMaker.make_expressions(piecedCode, outsideFunctions.copy() | functions.copy()) + list(functions.values())

    @staticmethod
    def make_command(line, functions, functionNames):
        command = {}
        if line[0] == 'for':
            if len(line) != 3:
                raise Exception(f"for statement {line} does not have: 'for', '(init, condition, increment)', 'code'")
            if len(line[1]) != 3:
                raise Exception(f"for statement {line} does not have: 'init', 'condition', 'increment'")
            command = {
                'type': 'for',
                'init': Piecer.make_command(line[1][0], functions, functionNames),
                'condition': Piecer.make_condition(line[1][1], functions, functionNames),
                'increment': Piecer.make_command(line[1][2], functions, functionNames),
                'code': Piecer.piece(line[2], functions, functionNames)
            }
        elif line[0] == 'if':
            if len(line) != 3:
                raise Exception(f"if statement {line} does not have: 'if', 'condition', 'code'")
            command = {
                'type': 'if',
                'condition': Piecer.make_condition(line[1], functions, functionNames),
                'code': Piecer.piece(line[2], functions, functionNames),
                'else': None
            }
        elif line[0] == 'elif':
            if len(line) != 3:
                raise Exception(f"elif statement {line} does not have: 'elif', 'condition', 'code'")
            command = {
                'type': 'elif',
                'condition': Piecer.make_condition(line[1], functions, functionNames),
                'code': Piecer.piece(line[2], functions, functionNames),
                'else': None
            }
        elif line[0] == 'else':
            if len(line) != 2:
                raise Exception(f"else statement {line} does not have: 'else', 'code'")
            command = {
                'type': 'else',
                'code': Piecer.piece(line[1], functions, functionNames),
            }
        elif line[0] == 'while':
            if len(line) != 3:
                raise Exception(f"while loop {line} does not have: 'while', 'condition', 'code'")
            command = {
                'type': 'while',
                'condition': Piecer.make_condition(line[1], functions, functionNames),
                'code': Piecer.piece(line[2], functions, functionNames)
            }
        elif line[0] == 'dowhile':
            if len(line) != 3:
                raise Exception(f"do while loop {line} does not have: 'do', 'condition', 'code', 'while'")
            command = {
                'type': 'dowhile',
                'code': Piecer.piece(line[2], functions, functionNames),
                'condition': Piecer.make_condition(line[1], functions, functionNames)
            }
        elif line[0] == 'print':
            if len(line) != 2:
                raise Exception(f"print statement {line} does not have: 'print', 'expression'")
            command = {
                'type': 'print',
                'expression': Piecer.make_expression(line[1], functions, functionNames)
            }
        elif line[0] == 'func':
            if len(line) != 4:
                raise Exception(f"function {line} does not have: 'func', 'name', ('args'), 'code'")
            command = {
                'type': 'function',
                'name': line[1],
                'replace': False,
                'params': line[2],
                'code': None,
                'return': None
            }
            command['code'] = Piecer.piece(line[3], functions | {line[1]: command}, [line[1]] + functionNames)
        elif line[0] == 'return':
            if len(line) == 1:
                command = {
                    'type': 'return',
                    'expression': None
                }
            else:
                if len(line) != 2:
                    raise Exception(f"function {line} does not have: 'return', ('expression')")
                if len(functionNames) == 0:
                    raise Exception(f'return statment {line} needs to be in a function')
                command = {
                    'type': 'return',
                    'expression': Piecer.make_expression(line[1], functions, functionNames)
                }
        elif line[0][:1] == '@':
            command = {
                'type': 'function setting',
                'text': line[0][1:]
            }
        elif len(line) > 1:
            if line[1] in ['=', '+=', '-=', '*=', '/=']:
                if len(line) < 3:
                    raise Exception(f"statement {line} does not have: 'var', 'operator', 'expression'")
                command = {
                    'type': '=',
                    'var': line[0],
                }
                if line[1] == '=':
                    command['expression'] = Piecer.make_expression(line[2:], functions, functionNames)
                else:
                    command['expression'] = Piecer.make_expression([line[0], line[1][:1], Piecer.make_expression(line[2:], functions, functionNames)], functions, functionNames)
            elif line[1] in ['++', '--']:
                if len(line) != 2:
                    raise Exception(f"statement {line} does not have: 'var', 'operator'")
                command = {
                    'type': '=',
                    'var': line[0],
                    'expression': Piecer.make_expression([line[0], line[1][:1], '1'], functions, functionNames)
                }
            elif line[0] in functions:
                if len(line) != 2:
                    raise Exception(f"statement {line} is wrongly called")
                if len(line[1]) != len(functions[line[0]]['params']):
                    raise Exception(f"statement {line} is does not have the params {functions[line[0]]['params']}")
                if line[0] in functionNames:
                    raise Exception(f"can not call function {line[0]} in side of {functionNames[0]}, function call path {functionNames}")
                command = {
                    'type': 'function call',
                    'name': line[0],
                    'args': Piecer.make_args(line[1], functions, functionNames),
                }
            else:
                raise Exception(f"could not find command {line}")
        elif line[0] in functions:
            if len(line) != 2:
                raise Exception(f"statement {line} is wrongly called")
            if len(line[1]) != len(functions[line[0]]['params']):
                raise Exception(f"statement {line} is does not have the params {functions[line[0]]['params']}")
            command = {
                'type': 'function call',
                'name': line[0],
                'args': Piecer.make_args(line[1], functions),
            }
        else:
            raise Exception(f"could not find command {line}")
        return command
    
    @staticmethod
    def make_args(args, functions, functionNames):
        newArgs = []
        for expression in args:
            newArgs.append(Piecer.make_expression(expression, functions, functionNames))
        return newArgs

    @staticmethod
    def make_expression(expression, functions, functionNames):
        i = 0
        while i < len(expression):
            item = expression[i]
            if item in tuple(functions.keys()):
                if len(expression) - 1 != i:
                    temp = expression[:i]
                    temp.append(Piecer.make_command(expression[i:i+2], functions, functionNames))
                    temp = temp + expression[i+2:]
                    expression = temp
            elif type(item) == list:
                expression[i] = Piecer.make_expression(expression[i], functions, functionNames)
            i+=1
        
        return {
            'type': 'expression',
            'expression': expression
            }
    
    def make_condition(expression, functions, functionNames):
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
                'expressionLeft': Piecer.make_expression(expressionSide1, functions, functionNames),
                'expressionRight': Piecer.make_expression(expressionSide2, functions, functionNames)
            }

    @staticmethod     
    def replace_functions(code, functions):
        lineNumber = 0
        while lineNumber < len(code):
            line = code[lineNumber]
            if line['type'] == 'function call':
                if line['name'] in functions:
                    if not line['name'] in functions:
                        code = Piecer.add_function(lineNumber, code, code[lineNumber], functions[line['name']])
            lineNumber += 1
        #expression scanner
        lineNumber = 0
        while lineNumber < len(code):
            line = code[lineNumber]
            code = Piecer.scan_expressions_func(line, code, functions, lineNumber)
            lineNumber += 1
        return code
    
    @staticmethod
    def scan_expressions_func(statements, code: list, functions: dict, lineNumber: int, parentStatement = None, key = None):
        if type(statements) == dict:
            i = 0
            while i < len(statements.keys()):
                k = list(statements.keys())[i]
                if ('expression' in k) or ('condition' in k):
                    code = Piecer.scan_expressions_func(statements[k], code, functions, lineNumber, statements, k)
                i += 1
            if statements['type'] == 'function call':
                if parentStatement != None:
                    parentStatement[key] = VariableNameGenerator.get_return_name(statements['name'])
                    code = Piecer.add_function(lineNumber, code, statements, functions[statements['name']], True)
        elif type(statements) == list:
            i = 0
            while i < len(statements):
                statement = statements[i]
                code = Piecer.scan_expressions_func(statement, code, functions, lineNumber, statements, i)
                i += 1
        return code

    @staticmethod
    def add_function(lineNumber: int, code: list, line: dict, function: dict, doReturn: bool = False):
        argI: int = 0
        funcCode: list = copy.deepcopy(function['code'])
        funcCode = Piecer.replaceVarNames(funcCode)
        for arg in line['args']:
            funcCode.insert(0, {'type': '=', 'var': function['params'][argI][0], 'expression': arg})
            argI += 1
        if not doReturn:
            del code[lineNumber]
            code = code[:lineNumber] + funcCode + code[lineNumber:]
        else:
            code = code[:lineNumber] + funcCode + code[lineNumber:]
        return code

    @staticmethod
    def replaceVarNames(code, start = ''):
        for line in code:
            pass #TODO: add code here
        return code