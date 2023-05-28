import json
from varNameGen import VariableNameGenerator

if __name__ == "__main__":
    import main

class ExpressionMaker:
    @staticmethod
    def make_expressions(code, functions):
        fixedCode = []
        for line in code:
            if not line['type'] in ExpressionMaker.commands:
                raise Exception(f"Error no command type {line['type']} found")
            fixedCode = ExpressionMaker.commands[line['type']](line, code, fixedCode)
        return fixedCode
    
    @staticmethod
    def make_expressions_for(line, code, fixedCode):
        #print('make_expressions_for')
        # init
        expressionCode, expression = ExpressionMaker.make_expression(line['init']['expression'], 'any')
        fixedCode = fixedCode + expressionCode
        line['init']['expression'] = expression
        fixedCode.append(line['init'])
        #condition
        line['conditionCode'] = {}
        for side in ['expressionLeft', 'expressionRight']:
            expressionCode, expression = ExpressionMaker.make_expression(line['condition'][side])
            line['condition'][side] = expression
            line['conditionCode'][side] = expressionCode
        #increment
        expressionCode, expression = ExpressionMaker.make_expression(line['increment']['expression'], 'any')
        line['code'] = line['code'] + expressionCode
        line['increment']['expression'] = expression
        line['code'].append(line['increment'])
        fixedCode.append({'type': 'while',
                          'comparator': line['condition']['comparator'],
                          'expressionLeft': line['condition']['expressionLeft'], 'expressionLeftCode': line['conditionCode']['expressionLeft'],
                          'expressionRight': line['condition']['expressionRight'], 'expressionRightCode': line['conditionCode']['expressionRight'],
                          'code': line['code']})
        return fixedCode
    
    @staticmethod
    def make_expressions_if(line, code, fixedCode):
        #print('make_expressions_if')
        for side in ['expressionLeft', 'expressionRight']:
            expressionCode, expression = ExpressionMaker.make_expression(line['condition'][side])
            line['condition'][side] = expression
            fixedCode = fixedCode + expressionCode
        fixedCode.append({'type': 'if', 'comparator': line['condition']['comparator'], 'expressionLeft': line['condition']['expressionLeft'], 'expressionRight': line['condition']['expressionRight'], 'code': line['code'], 'else': line['else']})
        return fixedCode
    
    @staticmethod
    def make_expressions_elif(line, code, fixedCode):
        #print('make_expressions_elif')
        for side in ['expressionLeft', 'expressionRight']:
            expressionCode, expression = ExpressionMaker.make_expression(line['condition'][side])
            line['condition'][side] = expression
            fixedCode = fixedCode + expressionCode
        fixedCode.append({'type': 'elif', 'comparator': line['condition']['comparator'], 'expressionLeft': line['condition']['expressionLeft'], 'expressionRight': line['condition']['expressionRight'], 'code': line['code'], 'else': line['else']})
        return fixedCode
    
    @staticmethod
    def make_expressions_else(line, code, fixedCode):
        #print("make_expressions_else")
        fixedCode.append({'type': 'else', 'code': line['code']})
        return fixedCode
    
    @staticmethod
    def make_expressions_while(line, code, fixedCode):
        #print("make_expressions_while")
        line['conditionCode'] = {}
        for side in ['expressionLeft', 'expressionRight']:
            expressionCode, expression = ExpressionMaker.make_expression(line['condition'][side])
            line['condition'][side] = expression
            line['conditionCode'][side] = expressionCode
            fixedCode = fixedCode + expressionCode
        fixedCode.append({'type': 'while', 
                          'comparator': line['condition']['comparator'],
                          'expressionLeft': line['condition']['expressionLeft'], 'expressionLeftCode': line['conditionCode']['expressionLeft'],
                          'expressionRight': line['condition']['expressionRight'], 'expressionRightCode': line['conditionCode']['expressionRight'],
                          'code': line['code']})
        return fixedCode
    
    @staticmethod
    def make_expressions_dowhile(line, code, fixedCode):
        #print("make_expressions_dowhile")
        line['conditionCode'] = {}
        for side in ['expressionLeft', 'expressionRight']:
            expressionCode, expression = ExpressionMaker.make_expression(line['condition'][side])
            line['condition'][side] = expression
            line['conditionCode'][side] = expressionCode
            fixedCode = fixedCode + expressionCode
        fixedCode.append({'type': 'dowhile', 
                          'comparator': line['condition']['comparator'],
                          'expressionLeft': line['condition']['expressionLeft'], 'expressionLeftCode': line['conditionCode']['expressionLeft'],
                          'expressionRight': line['condition']['expressionRight'], 'expressionRightCode': line['conditionCode']['expressionRight'],
                          'code': line['code']})
        return fixedCode
    
    @staticmethod
    def make_expressions_print(line, code, fixedCode):
        #print("make_expressions_print")
        expressionCode, expression = ExpressionMaker.make_expression(line['expression']['expression'])
        command = {'type': 'print', 'expression': expression}
        fixedCode = fixedCode + expressionCode
        fixedCode.append(command)
        return fixedCode
    
    @staticmethod
    def make_expressions_function(line, code, fixedCode):
        #pretty sure this cant run...
        #print("make_expressions_function")
        return fixedCode
    
    @staticmethod
    def make_expressions_return(line, code, fixedCode):
        #print("make_expressions_return")
        if line['expression'] == None:
            fixedCode.append({'type': 'return', 'expression': None})
        else:
            expressionCode, expression = ExpressionMaker.make_expression(line['expression'])
            command = {'type': 'return', 'expression': expression}
            fixedCode = fixedCode +  expressionCode
            fixedCode.append(command)
        return fixedCode
    
    @staticmethod
    def make_expressions_function_setting(line, code, fixedCode):
        #print("make_expressions_function_setting")
        # do not append because we dont need function setting after we added them to the functions earlier
        #fixedCode.append(line)
        return fixedCode
    
    @staticmethod
    def make_expressions_set(line, code, fixedCode):
        #print("make_expressions_set")
        expressionCode, expression = ExpressionMaker.make_expression(line['expression'], 'any')
        command = {'type': '=', 'var': line['var'], 'expression': expression}
        fixedCode = fixedCode +  expressionCode
        fixedCode.append(command)
        return fixedCode
    
    @staticmethod
    def make_expressions_function_call(line, code, fixedCode):
        #print("make_expressions_function_call")
        i = 0
        for arg in line['args']:
            expressionCode, expression = ExpressionMaker.make_expression(arg)
            line['args'][i] = expression
            fixedCode = fixedCode + expressionCode
            i += 1
        fixedCode.append({'type': 'function call', 'name': line['name'], 'args': line['args']})
        return fixedCode
        
    commands = {
        'for': make_expressions_for,
        'if': make_expressions_if,
        'elif': make_expressions_elif,
        'else': make_expressions_else,
        'while': make_expressions_while,
        'dowhile': make_expressions_dowhile,
        'print': make_expressions_print,
        'function': make_expressions_function,
        'return': make_expressions_return,
        'function setting': make_expressions_function_setting,
        '=': make_expressions_set,
        'function call': make_expressions_function_call,  
    }
    
    def get_expression_block(expression):
        if len(expression) % 2 == 0:
            raise Exception(f"invaild expression {expression}")
        if len(expression) == 1:
            if type(expression[0]) == list:
                return ExpressionMaker.get_expression_block(expression[0])
            else:
                return expression
        itemTrio = []
        i = 0
        for item in expression:
            itemTrio.append(item)
            i += 1
            if i >= 3:
                temp = itemTrio.copy()
                itemTrio = []
                itemTrio.append(temp)
                i = 1
        return itemTrio[0]
    
    @staticmethod
    def make_expression(expression, typeNeeded = '1 num or var'):
        while type(expression) == dict and expression['type'] == 'expression':
            expression = expression['expression']
        if type(expression) != list:
            expression = [expression]
        if len(expression) % 2 == 0:
            raise Exception(f"invaild expression {expression}")
        if typeNeeded == '1 num or var':
            block = ExpressionMaker.get_expression_block(expression)
            if len(block) == 1:
                return [], block[0]
            else:
                var = VariableNameGenerator.gen_name()
                code, value = ExpressionMaker.make_expression(block, 'any')
                command = {'type': '=', 'var': var, 'expression': value}
                code.append(command)
                return code, var
        elif typeNeeded == 'any':
            block = ExpressionMaker.get_expression_block(expression)
            if len(block) == 1:
                return [], block[0]
            else:
                i = 0
                code = []
                for item in block:
                    while type(item) == dict and item['type'] == 'expression':
                        item = item['expression']
                    if type(item) == list:
                        itemBlock = ExpressionMaker.get_expression_block(item)
                        if len(itemBlock) == 1:
                            block[i] = itemBlock[0]
                        else:
                            var = VariableNameGenerator.gen_name()
                            itemCode, value = ExpressionMaker.make_expression(itemBlock, 'any')
                            command = {'type': '=', 'var': var, 'expression': value}
                            code = code + itemCode
                            code.append(command)
                            block[i] = var
                    else:
                        block[i] = item
                    i += 1
                return code, block
        else:
            raise Exception(f"could not find typeNeeded type {typeNeeded} in make_expression for expression {expression}")