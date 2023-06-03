from varNameManager import VariableNameManager

if __name__ == "__main__":
    import main

class SingleCommandMaker:
    @staticmethod
    def make_command(line, functions, functionNames):
        command = {}
        if line[0] == 'for':
            if len(line) != 3:
                raise Exception(f"for statement {line} does not have: 'for', '(init, condition, increment)', 'code'")
            if len(line[1]) != 3:
                raise Exception(f"for statement {line} does not have: 'init', 'condition', 'increment'")
            from piecer import Piecer
            command = {
                'type': 'for',
                'init': SingleCommandMaker.make_command(line[1][0], functions, functionNames),
                'condition': SingleCommandMaker.make_condition(line[1][1], functions, functionNames),
                'increment': SingleCommandMaker.make_command(line[1][2], functions, functionNames),
                'code': Piecer.piece(line[2], functions, functionNames)
            }
        elif line[0] == 'if':
            if len(line) < 3:
                raise Exception(f"if statement {line} does not have: 'if', 'condition', 'code'")
            from piecer import Piecer
            code = line[2:]
            while type(code) == list and len(code) == 1 and type(code[0]) == list and (len(code[0]) == 1 or type(code[0][0]) == list):
                code = code[0]
            while type(code) == list and type(code[0]) != list:
                code = [code]
            command = {
                'type': 'if',
                'condition': SingleCommandMaker.make_condition(line[1], functions, functionNames),
                'code': Piecer.piece(code, functions, functionNames),
                'else': None
            }
        elif line[0] == 'elif':
            if len(line) < 3:
                raise Exception(f"elif statement {line} does not have: 'elif', 'condition', 'code'")
            from piecer import Piecer
            code = line[2:]
            while type(code) == list and len(code) == 1 and type(code[0]) == list and (len(code[0]) == 1 or type(code[0][0]) == list):
                code = code[0]
            while type(code) == list and type(code[0]) != list:
                code = [code]
            command = {
                'type': 'elif',
                'condition': SingleCommandMaker.make_condition(line[1], functions, functionNames),
                'code': Piecer.piece(code, functions, functionNames),
                'else': None
            }
        elif line[0] == 'else':
            if len(line) < 2:
                raise Exception(f"else statement {line} does not have: 'else', 'code'")
            from piecer import Piecer
            code = line[1:]
            while type(code) == list and len(code) == 1 and type(code[0]) == list and (len(code[0]) == 1 or type(code[0][0]) == list):
                code = code[0]
            while type(code) == list and type(code[0]) != list:
                code = [code]
            command = {
                'type': 'else',
                'code': Piecer.piece(code, functions, functionNames),
            }
        elif line[0] == 'while':
            if len(line) != 3:
                raise Exception(f"while loop {line} does not have: 'while', 'condition', 'code'")
            from piecer import Piecer
            command = {
                'type': 'while',
                'condition': SingleCommandMaker.make_condition(line[1], functions, functionNames),
                'code': Piecer.piece(line[2], functions, functionNames)
            }
        elif line[0] == 'dowhile':
            if len(line) != 3:
                raise Exception(f"do while loop {line} does not have: 'do', 'condition', 'code', 'while'")
            from piecer import Piecer
            command = {
                'type': 'dowhile',
                'code': Piecer.piece(line[2], functions, functionNames),
                'condition': SingleCommandMaker.make_condition(line[1], functions, functionNames)
            }
        elif line[0] == 'print':
            if len(line) != 2:
                raise Exception(f"print statement {line} does not have: 'print', 'expression'")
            command = {
                'type': 'print',
                'expression': SingleCommandMaker.make_expression(line[1], functions, functionNames)
            }
        elif line[0] == 'func':
            if len(line) != 4:
                raise Exception(f"function {line} does not have: 'func', 'name', ('args'), 'code'")
            line[1] = line[1] + '_param_count:' + str(len(line[2]))
            if line[1] in functions:
                raise Exception(f"function '{line[1]}({line[2]})' can not be declared twise in the same scope")
            command = {
                'type': 'function',
                'name': line[1],
                'replace': False,
                'params': VariableNameManager.replace_var_names(line[2], 'USR'),
                'code': None,
                'return': None
            }
            from piecer import Piecer
            functionCode = Piecer.piece(line[3], functions | {line[1]: command}, [line[1]] + functionNames)
            functionCode.insert(0, {'type': 'define', 'var':command['returnName']})
            command['code'] = functionCode
        elif line[0] == 'raw':
            if len(line) != 2:
                raise Exception(f"raw code {line} does not have: 'raw', {'code'}")
        elif line[0] == 'define':
            if len(line) != 2:
                raise Exception(f"define {line} does not have: 'define', 'var")
            command = {
                'type': 'define',
                'var': line[1],
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
                if len(functionNames) == 0:
                    raise Exception(f'return statment {line} needs to be in a function')
                command = {
                    'type': 'return',
                    'expression': SingleCommandMaker.make_expression(line[1], functions, functionNames)
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
                    command['expression'] = SingleCommandMaker.make_expression(line[2:], functions, functionNames)
                else:
                    command['expression'] = SingleCommandMaker.make_expression([line[0], line[1][:1], SingleCommandMaker.make_expression(line[2:], functions, functionNames)], functions, functionNames)
            elif line[1] in ['++', '--']:
                if len(line) != 2:
                    raise Exception(f"statement {line} does not have: 'var', 'operator'")
                command = {
                    'type': '=',
                    'var': line[0],
                    'expression': SingleCommandMaker.make_expression([line[0], line[1][:1], '1'], functions, functionNames)
                }
            else:
                print(line)
                if line[0] + '_param_count:' + str(len(line[1])) in functions:
                    if len(line) != 2:
                        raise Exception(f"statement {line} is wrongly called")
                    line[0] = line[0] + '_param_count:' + str(len(line[1]))
                    if len(line[1]) != len(functions[line[0]]['params']):
                        raise Exception(f"statement {line} is does not have the params {functions[line[0]]['params']}")
                    if line[0] in functionNames:
                        raise Exception(f"can not call function {line[0]} in side of {functionNames[0]}, function call path {functionNames}")
                    command = {
                        'type': 'function call',
                        'name': line[0],
                        'args': SingleCommandMaker.make_args(line[1], functions, functionNames),
                    }
                else:
                    raise Exception(f"could not find command {line}")
        else:
            raise Exception(f"could not find command {line}")
        return command
    
    @staticmethod
    def make_args(args, functions, functionNames):
        newArgs = []
        for expression in args:
            newArgs.append(SingleCommandMaker.make_expression(expression, functions, functionNames))
        return newArgs

    @staticmethod
    def make_expression(expression, functions, functionNames):
        i = 0
        while i < len(expression):
            item = expression[i]
            if len(expression) - i > 1:
                if type(item) == list:
                    expression[i] = SingleCommandMaker.make_expression(expression[i], functions, functionNames)
                elif item + '_param_count:' + str(len(expression[i+1])) in tuple(functions.keys()):
                    temp:list = expression[:i]
                    temp.append(SingleCommandMaker.make_command(expression[i:i+2], functions, functionNames))
                    temp = temp + expression[i+2:]
                    expression = temp                    
            elif type(item) == list:
                    expression[i] = SingleCommandMaker.make_expression(expression[i], functions, functionNames)
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
        if len(expression) == 1:
            if expression in ['<', '>', '==', '!=', '<=', '>=']:
                raise Exception(f"condition {expression} need to have a expression on both sides of the operator")
            else:
                expression = [SingleCommandMaker.make_expression(expression, functions, functionNames), '!=', '0']
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
                'expressionLeft': SingleCommandMaker.make_expression(expressionSide1, functions, functionNames),
                'expressionRight': SingleCommandMaker.make_expression(expressionSide2, functions, functionNames)
            }
