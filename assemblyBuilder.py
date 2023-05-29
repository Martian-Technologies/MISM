import copy
import operator
from varNameGen import VariableNameGenerator

if __name__ == "__main__":
    import main

class AssemblyBuilder:
    vars = {}
    
    @staticmethod
    def make_assembly(code, doPrint = False):
        assemblyCode = []
        for line in code:
            if not line['type'] in AssemblyBuilder.commands:
                raise Exception(f"Error no command type {line['type']} found")
            assemblyCode = AssemblyBuilder.commands[line['type']](line, assemblyCode)
        if doPrint:
            print(AssemblyBuilder.vars)
        return assemblyCode
    
    @staticmethod
    def make_assembly_if(line, assemblyCode):
        #print('make_assembly_if')
        AssemblyBuilder.checkValidExpressionItem(line['expressionLeft'])
        AssemblyBuilder.checkValidExpressionItem(line['expressionRight'])
        if AssemblyBuilder.is_number(line['expressionLeft']):
            varName = VariableNameGenerator.gen_name()
            assemblyCode.append(f"SET {AssemblyBuilder.getVarID(varName)} {line['expressionLeft']}")
            line['expressionLeft'] = varName
        if AssemblyBuilder.is_number(line['expressionRight']):
            varName = VariableNameGenerator.gen_name()
            assemblyCode.append(f"SET {AssemblyBuilder.getVarID(varName)} {line['expressionRight']}")
            line['expressionRight'] = varName
        skipJumpName = AssemblyBuilder.gen_jump_name()
        oppositeComparators = {'==': '!=', '!=': '==', '<=': '>', '>': '<=', '>=': '<', '<': '>='}
        assemblyCode.append(f"JMIF {oppositeComparators[line['comparator']]} {AssemblyBuilder.getVarID(line['expressionLeft'])} {AssemblyBuilder.getVarID(line['expressionRight'])} ~{skipJumpName}")
        assemblyCode = assemblyCode + AssemblyBuilder.make_assembly(line['code'])
        if line['else'] != None:
            skipElseJumpName = AssemblyBuilder.gen_jump_name()
            assemblyCode.append(f"RJMP ~{skipElseJumpName}")
            assemblyCode.append(f"{skipJumpName}:")
            assemblyCode = assemblyCode + AssemblyBuilder.make_assembly(line['else']['code'])
            assemblyCode.append(f"{skipElseJumpName}:")
        else:
            assemblyCode.append(f"{skipJumpName}:")
        return assemblyCode

    @staticmethod
    def make_assembly_while(line, assemblyCode):
        #print('make_assembly_while')
        assemblyCodeLeft = AssemblyBuilder.make_assembly(line['expressionLeftCode'])
        AssemblyBuilder.checkValidExpressionItem(line['expressionLeft'])
        assemblyCodeRight = AssemblyBuilder.make_assembly(line['expressionRightCode'])
        AssemblyBuilder.checkValidExpressionItem(line['expressionRight'])
        assemblyCode = assemblyCode + assemblyCodeLeft
        assemblyCode = assemblyCode + assemblyCodeRight
        if AssemblyBuilder.is_number(line['expressionLeft']):
            varName = VariableNameGenerator.gen_name()
            assemblyCode.append(f"SET {AssemblyBuilder.getVarID(varName)} {line['expressionLeft']}")
            line['expressionLeft'] = varName
        if AssemblyBuilder.is_number(line['expressionRight']):
            varName = VariableNameGenerator.gen_name()
            assemblyCode.append(f"SET {AssemblyBuilder.getVarID(varName)} {line['expressionRight']}")
            line['expressionRight'] = varName
        skipJumpName = AssemblyBuilder.gen_jump_name()
        oppositeComparators = {'==': '!=', '!=': '==', '<=': '>', '>': '<=', '>=': '<', '<': '>='}
        assemblyCode.append(f"JMIF {oppositeComparators[line['comparator']]} {AssemblyBuilder.getVarID(line['expressionLeft'])} {AssemblyBuilder.getVarID(line['expressionRight'])} ~{skipJumpName}")
        repeatJumpName = AssemblyBuilder.gen_jump_name()
        assemblyCode.append(f"{repeatJumpName}:")
        assemblyCode = assemblyCode + AssemblyBuilder.make_assembly(line['code'])
        assemblyCode = assemblyCode + assemblyCodeLeft
        assemblyCode = assemblyCode + assemblyCodeRight
        assemblyCode.append(f"JMIF {line['comparator']} {AssemblyBuilder.getVarID(line['expressionLeft'])} {AssemblyBuilder.getVarID(line['expressionRight'])} ~{repeatJumpName}")
        assemblyCode.append(f"{skipJumpName}:")
        return assemblyCode
    
    @staticmethod
    def make_assembly_dowhile(line, assemblyCode):
        #print('make_assembly_dowhile')
        assemblyCodeLeft = AssemblyBuilder.make_assembly(line['expressionLeftCode'])
        AssemblyBuilder.checkValidExpressionItem(line['expressionLeft'])
        assemblyCodeRight = AssemblyBuilder.make_assembly(line['expressionRightCode'])
        AssemblyBuilder.checkValidExpressionItem(line['expressionRight'])
        if AssemblyBuilder.is_number(line['expressionLeft']):
            varName = VariableNameGenerator.gen_name()
            assemblyCodeLeft.append(f"SET {AssemblyBuilder.getVarID(varName)} {line['expressionLeft']}")
            line['expressionLeft'] = varName
        if AssemblyBuilder.is_number(line['expressionRight']):
            varName = VariableNameGenerator.gen_name()
            assemblyCodeRight.append(f"SET {AssemblyBuilder.getVarID(varName)} {line['expressionRight']}")
            line['expressionRight'] = varName
        repeatJumpName = AssemblyBuilder.gen_jump_name()
        assemblyCode.append(f"{repeatJumpName}:")
        assemblyCode = assemblyCode + AssemblyBuilder.make_assembly(line['code'])
        assemblyCode = assemblyCode + assemblyCodeLeft
        assemblyCode = assemblyCode + assemblyCodeRight
        assemblyCode.append(f"JMIF {line['comparator']} {AssemblyBuilder.getVarID(line['expressionLeft'])} {AssemblyBuilder.getVarID(line['expressionRight'])} ~{repeatJumpName}")
        return assemblyCode
    
    @staticmethod
    def make_assembly_print(line, assemblyCode):
        #print('make_assembly_print')
        AssemblyBuilder.checkValidExpressionItem(line['expression'])
        if AssemblyBuilder.is_number(line['expression']):
            assemblyCode.append(f"PRI {line['expression']}")
        else:
            assemblyCode.append(f"PRIA {AssemblyBuilder.getVarID(line['expression'])}")
        return assemblyCode
    
    @staticmethod
    def make_assembly_function(line, assemblyCode):
        #print('make_assembly_function')
        return assemblyCode
    
    @staticmethod
    def make_assembly_return(line, assemblyCode):
        #print('make_assembly_return')
        return assemblyCode
    
    @staticmethod
    def make_assembly_set(line, assemblyCode):
        #print('make_assembly_set')
        setVarID = AssemblyBuilder.getVarID(line['var'])
        if type(line['expression']) != list:
            line['expression'] = [line['expression']]
        if len(line['expression']) == 1:
            AssemblyBuilder.checkValidExpressionItem(line['expression'][0])
            if AssemblyBuilder.is_number(line['expression'][0]):
                assemblyCode.append(f"SET {setVarID} {line['expression'][0]}")
            else:
                assemblyCode.append(f"M {AssemblyBuilder.getVarID(line['expression'][0])} {setVarID}")
        else:
            AssemblyBuilder.checkValidExpressionItem(line['expression'][0])
            AssemblyBuilder.checkValidExpressionItem(line['expression'][2])
            if AssemblyBuilder.is_number(line['expression'][0]):
                if AssemblyBuilder.is_number(line['expression'][2]):
                    num = AssemblyBuilder.operatorFunctions[line['expression'][1]](float(line['expression'][0]), float(line['expression'][2]))
                    assemblyCode.append(f"SET {setVarID} {num}")
                else:
                    swaps = {'-': 'r-', '/': 'r/', '%': 'r%', '6': 'r^'}
                    if line['expression'][1] in swaps:
                        line['expression'][1] = swaps[line['expression'][1]]
                    assemblyCode.append(f"ONC {line['expression'][1]} {AssemblyBuilder.getVarID(line['expression'][2])} {line['expression'][0]} {setVarID}")
                
            elif AssemblyBuilder.is_number(line['expression'][2]):
                assemblyCode.append(f"ONC {line['expression'][1]} {AssemblyBuilder.getVarID(line['expression'][0])} {line['expression'][2]} {setVarID}")
            else:
                assemblyCode.append(f"OPR {line['expression'][1]} {AssemblyBuilder.getVarID(line['expression'][0])} {AssemblyBuilder.getVarID(line['expression'][2])} {setVarID}")
        return assemblyCode
    
    @staticmethod
    def make_assembly_function_call(line, assemblyCode):
        #print('make_assembly_function_call')
        return assemblyCode

    def make_assembly_define(line, assemblyCode):
        #print('make_assembly_define')
        AssemblyBuilder.getVarID(line['var'])
        return assemblyCode
    
    commands = {
        'if': make_assembly_if,
        'while': make_assembly_while,
        'dowhile': make_assembly_dowhile,
        'print': make_assembly_print,
        'function': make_assembly_function,
        'return': make_assembly_return,
        '=': make_assembly_set,
        'function call': make_assembly_function_call,
        'define': make_assembly_define
    }
    
    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def getVarID(name):
        if not AssemblyBuilder.isValidVarName(name):
            raise Exception(f"var name {name} is not a valid var name")
        if name in AssemblyBuilder.vars:
            return AssemblyBuilder.vars[name]
        else:
            AssemblyBuilder.vars[name] = len(AssemblyBuilder.vars.keys())
            return AssemblyBuilder.vars[name]
    
    @staticmethod
    def isValidVarName(name):
        if AssemblyBuilder.is_number(name) or type(name) != str:
            return False
        return True
    
    @staticmethod
    def checkValidExpressionItem(item):
        if type(item) != str or (not ((item in list(AssemblyBuilder.vars.keys())) or AssemblyBuilder.is_number(item))):
            raise Exception(f"expression item {item} is not valid")
        
    operatorFunctions = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv, '%': operator.mod, '^': operator.pow}
    
    numberOfJumpNames = 0
    
    @staticmethod
    def gen_jump_name(start = ''):
        AssemblyBuilder.numberOfJumpNames += 1
        return start + '_jump_⭳ⲼⱢ╴⾈⿗⦷ⲟ_ID:_' + str(AssemblyBuilder.numberOfJumpNames)