import json
from varNameManager import VariableNameManager

if __name__ == "__main__":
    import main

class ExpressionMaker:
    @staticmethod
    def make_expressions(code, functions):
        fixedCode = []
        for line in code:
            if not line['type'] in ExpressionMaker.commands:
                raise Exception(f"Error no command type {line['type']} found")
            fixedCode = ExpressionMaker.commands[line['type']](line, fixedCode)
        return fixedCode
    
    @staticmethod
    def make_expressions_for(line, fixedCode):
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
    def make_expressions_if(line, fixedCode):
        #print('make_expressions_if')
        for side in ['expressionLeft', 'expressionRight']:
            expressionCode = None
            expression = None
            if 'condition' in line:
                expressionCode, expression = ExpressionMaker.make_expression(line['condition'][side])
                line['condition'][side] = expression
            else:
                expressionCode, expression = ExpressionMaker.make_expression(line[side])
                line[side] = expression
            
            fixedCode = fixedCode + expressionCode
        elseCode = None
        if line['else'] != None:
            if line['else']['type'] == 'elif':
                elseCode = {'type': 'else', 'code': ExpressionMaker.make_expressions_elif(line['else'], [])}
            elif line['else']['type'] == 'else':
                elseCode = line['else']
        if 'condition' in line:
            fixedCode.append({
                'type': 'if',
                'comparator': line['condition']['comparator'],
                'expressionLeft': line['condition']['expressionLeft'],
                'expressionRight': line['condition']['expressionRight'],
                'code': line['code'], 'else': elseCode
            })
        else:
            fixedCode.append({
                'type': 'if',
                'comparator': line['comparator'],
                'expressionLeft': line['expressionLeft'],
                'expressionRight': line['expressionRight'],
                'code': line['code'], 'else': elseCode
            })
        return fixedCode
    
    @staticmethod
    def make_expressions_elif(line, fixedCode):
        #print('make_expressions_elif')
        fixedCode = ExpressionMaker.make_expressions_if(line, fixedCode)
        return fixedCode
    
    @staticmethod
    def make_expressions_else(line, fixedCode):
        #print("make_expressions_else")
        fixedCode.append({'type': 'else', 'code': line['code']})
        return fixedCode
    
    @staticmethod
    def make_expressions_while(line, fixedCode):
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
    def make_expressions_dowhile(line, fixedCode):
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
    def make_expressions_print(line, fixedCode):
        #print("make_expressions_print")
        expressionCode, expression = ExpressionMaker.make_expression(line['expression'])
        command = {'type': 'print', 'expression': expression}
        fixedCode = fixedCode + expressionCode
        fixedCode.append(command)
        return fixedCode
    
    @staticmethod
    def make_expressions_function(line, fixedCode):
        #pretty sure this cant run...
        #print("make_expressions_function")
        return fixedCode
    
    @staticmethod
    def make_expressions_return(line, fixedCode):
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
    def make_expressions_function_setting(line, fixedCode):
        #print("make_expressions_function_setting")
        # do not append because we dont need function setting after we added them to the functions earlier
        #fixedCode.append(line)
        return fixedCode
    
    @staticmethod
    def make_expressions_set(line, fixedCode):
        #print("make_expressions_set")
        expressionCode, expression = ExpressionMaker.make_expression(line['expression'], 'any')
        command = {'type': '=', 'var': line['var'], 'expression': expression}
        fixedCode = fixedCode +  expressionCode
        fixedCode.append(command)
        return fixedCode
    
    @staticmethod
    def make_expressions_function_call(line, fixedCode):
        #print("make_expressions_function_call")
        i = 0
        for arg in line['args']:
            expressionCode, expression = ExpressionMaker.make_expression(arg)
            line['args'][i] = expression
            fixedCode = fixedCode + expressionCode
            i += 1
        fixedCode.append({'type': 'function call', 'name': line['name'], 'args': line['args']})
        return fixedCode
    
    @staticmethod
    def make_expressions_define(line, fixedCode):
        #print("make_expressions_define")
        command = {'type': 'define', 'var': line['var']}
        fixedCode.append(command)
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
        'define': make_expressions_define
    }
    
    def get_expression_block(expression):
        #if len(expression) % 2 == 0:
        #    raise Exception(f"invaild expression {expression}")
        if len(expression) == 1:
            if type(expression[0]) == list:
                return ExpressionMaker.get_expression_block(expression[0])
            else:
                if type(expression[0]) == dict and expression[0]['type'] == 'expression':
                    expression = ExpressionMaker.get_expression_block(expression[0]['expression'])
                return expression
        itemTrio = []
        i = 0
        operators = ['+', '-', '*', '/', '%', '^', '==', '>', '>=', '<', '<=']
        for item in expression:
            if len(itemTrio) == i:
                itemTrio.append(item)
            else:
                itemTrio[i] += item
            i += 1
            if i == 2:
                if not item in operators:
                    raise Exception(f"{item} is not a valid operator in an expression")
            else:
                if item == '*':
                    i -= 1
                elif type(item) == str and not (VariableNameManager.isValidVarName(item), VariableNameManager.is_number(item)):
                    raise Exception(f"{item} is not a valid number or variable in an expression")
            if i >= 3:
                temp = itemTrio.copy()
                itemTrio = []
                itemTrio.append(temp)
                i = 1
        return itemTrio[0]
    
    @staticmethod
    def make_expression(expression, typeNeeded = '1 num or var'):
        #setup
        while type(expression) == dict and expression['type'] == 'expression':
            expression = expression['expression']
        if type(expression) != list:
            expression = [expression]
        if len(expression) % 2 == 0:
            raise Exception(f"invaild expression {expression}")
        #to different algrithems for each typeNeeded
        if typeNeeded == '1 num or var':
            block = ExpressionMaker.get_expression_block(expression)
            if len(block) == 1:
                while type(block[0]) == dict and block[0]['type'] == 'expression':
                    block[0] = block[0]['expression']
                return [], block[0]
            else:
                var = VariableNameManager.gen_name()
                code, value = ExpressionMaker.make_expression(block, 'any')
                command = {'type': '=', 'var': var, 'expression': value}
                code.append(command)
                return code, var
        elif typeNeeded == 'any':
            block = ExpressionMaker.get_expression_block(expression)
            if len(block) == 1:
                return [], block[0]
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
                        var = VariableNameManager.gen_name()
                        itemCode, value = ExpressionMaker.make_expression(itemBlock, 'any')
                        command = {'type': '=', 'var': var, 'expression': value}
                        code = code + itemCode
                        code.append(command)
                        block[i] = var
                elif type(item) == dict:
                    if item['type'] == 'function call':
                        newArgs = []
                        for arg in item['args']:
                            itemCode, value = ExpressionMaker.make_expression(arg)
                            code = code + itemCode
                            newArgs.append(value)
                        command = {'type': 'function call', 'name': item['name'], 'expression': newArgs}
                        block[i] = command
                    else:
                        raise Exception(f"can not use {item} in expressions")
                else:
                    block[i] = item
                i += 1
            return code, block
        else:
            raise Exception(f"could not find typeNeeded type {typeNeeded} in make_expression for expression {expression}")