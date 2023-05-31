import json
from expressionMaker import ExpressionMaker
from VarNameManager import VariableNameManager
from functionManager import FunctionManager
from singleCommandMaker import SingleCommandMaker

if __name__ == "__main__":
    import main

class Piecer:
    @staticmethod
    def piece(parsedCode, outsideFunctions = {}, functionNames = [], isFunction = False):
        functions = {}
        i = 0
        piecedCode = []
        setReturn = False
        while i < len(parsedCode):
            codeLine = parsedCode[i]
            command = SingleCommandMaker.make_command(codeLine, outsideFunctions.copy() | functions.copy(), functionNames)
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
                    piecedCode.append({'type': '=', 'var': VariableNameManager.get_return_name(functionNames[0]), 'expression': command['expression']})
                    piecedCode.insert(0, {'type': 'define', 'var': VariableNameManager.get_return_name(functionNames[0])})
                    setReturn = True
            else:
                piecedCode.append(command)
            i += 1
        piecedCode = VariableNameManager.replace_var_names(piecedCode, 'USR')
        piecedCode = FunctionManager.replace_functions(piecedCode, outsideFunctions.copy() | functions.copy())
        if setReturn:
            outsideFunctions[functionNames[0]]['returnName'] = piecedCode[0]['var']
            del piecedCode[0]
        for name in list(functions.keys()).copy():
            if functions[name]['replace']:
                del functions[name]
        return ExpressionMaker.make_expressions(piecedCode, outsideFunctions.copy() | functions.copy()) + list(functions.values())
