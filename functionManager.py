import copy
from varNameManager import VariableNameManager

if __name__ == "__main__":
    import main

class FunctionManager:
    @staticmethod     
    def replace_functions(code, functions):
        lineNumber = 0
        while lineNumber < len(code):
            line = code[lineNumber]
            if line['type'] == 'function call':
                if line['name'] in functions:
                    if not line['name'] in functions:
                        code = FunctionManager.add_function(lineNumber, code, code[lineNumber], functions[line['name']])
            lineNumber += 1
        #expression scanner
        lineNumber = 0
        while lineNumber < len(code):
            line = code[lineNumber]
            code, lineNumber = FunctionManager.scan_expressions_func(line, code, functions, lineNumber)
            lineNumber += 1
        return code
    
    @staticmethod
    def scan_expressions_func(statements, code: list, functions: dict, lineNumber: int, parentStatement = None, key = None):
        if type(statements) == dict:
            i = 0
            while i < len(statements.keys()):
                k = list(statements.keys())[i]
                if ('expression' in k) or ('condition' in k) or ('args' in k):
                    code, lineNumber = FunctionManager.scan_expressions_func(statements[k], code, functions, lineNumber, statements, k)
                i += 1
            if statements['type'] == 'function call':
                if parentStatement != None:
                    VariableNameManager.returnNameID += 1
                    code, returnName, lineNumber = FunctionManager.add_function(lineNumber, code, statements, functions[statements['name']], True)
                    parentStatement[key] = returnName
        elif type(statements) == list:
            i = 0
            while i < len(statements):
                statement = statements[i]
                code, lineNumber = FunctionManager.scan_expressions_func(statement, code, functions, lineNumber, statements, i)
                i += 1
        return code, lineNumber

    @staticmethod
    def add_function(lineNumber: int, code: list, line: dict, function: dict, doReturn: bool = False):
        funcCode: list = copy.deepcopy(function['code'])
        argI: int = 0
        for arg in line['args']:
            funcCode.insert(1, {'type': '=', 'var': function['params'][argI][0], 'expression': {'temp': arg}})
            argI += 1
        funcCode = VariableNameManager.replace_var_names(funcCode, f"{function['name']}:{VariableNameManager.get_new_func_ID()}", deepScan=True)
        argI = 0
        while argI < len(line['args']):
            funcCode[1 + argI]['expression'] = funcCode[1 + argI]['expression']['temp']
            argI += 1
        returnName = None
        if doReturn:
            returnName = funcCode[0]['var']
        if not doReturn:
            del code[lineNumber]
            code = code[:lineNumber] + funcCode + code[lineNumber:]
        else:
            code = code[:lineNumber] + funcCode + code[lineNumber:]
        return code, returnName, lineNumber + len(funcCode)