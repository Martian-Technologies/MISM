from copy import copy
from varNameManager import VariableNameManager

if __name__ == "__main__":
    import main

class OptimizerUtil:
    @staticmethod
    def follow_index_stack(code, indexStack):
        out = code
        for k in indexStack:
            out = out[k]
        return out
    
    @staticmethod
    def follow_index_stack_set(code, indexStack, value):
        if len(indexStack) == 0:
            return value
        code[indexStack[0]] = OptimizerUtil.follow_index_stack_set(code[indexStack[0]], indexStack[1:], value)
        return code
    
    @staticmethod
    def get_code_stack(stack):
        """Shortens the stack to just point to a code line (not a expression, var...)"""
        codeStack = []
        for k in stack:
            if k in ['expression', 'condition', 'args', 'var']:
                break
            codeStack.append(k)
        return codeStack
    
    @staticmethod
    def get_path_relative(path1, path2):
        """
        If the paths are in the SAME scope it returns 'same'\n
        If path1 is in a scope that path2 ends in it returns 'p1 in p2'\n
        If path2 is in a scope that path1 ends in it returns 'p2 in p1'\n
        If the paths are not connected it returns 'none'
        """
        path1 = OptimizerUtil.get_code_stack(path1)
        path2 = OptimizerUtil.get_code_stack(path2)
        searchLen = len(path1)
        if len(path1) > len(path2):
            searchLen = len(path2)
        i = 0
        while i < searchLen:
            if path1[i] != path2[i]:
                return 'none'
            i+=1
        if len(path1) > len(path2):
            return 'p1 in p2'
        elif len(path1) < len(path2):
            return 'p2 in p1'
        else:
            return 'same'
    
    @staticmethod
    def removeCommand(code:list, stack:list):
        codeStack = OptimizerUtil.get_code_stack(stack)
        if len(codeStack) == 0:
            raise Exception(f"can not remove command at {stack} because it does not goto a command")
        listWithLine = OptimizerUtil.follow_index_stack(code, codeStack[:-1])
        del listWithLine[codeStack[-1]]
        code = OptimizerUtil.follow_index_stack_set(code, codeStack[:-1], listWithLine)
        return code
    
    @staticmethod
    def get_var_usages(code, usageType = 'any'):
        def get_var_usages_scan(code:list, indexStack:list, varUsageDict:dict, usageType:str):
            block = OptimizerUtil.follow_index_stack(code, indexStack)
            if type(block) == dict:
                i = 0
                while i < len(block.keys()):
                    k = list(block.keys())[i]
                    if usageType == 'any':
                        if ('expression' in k) or ('condition' in k) or ('args' in k) or ('var' in k) or ('code' in k) or ('else' in k):
                            varUsageDict = get_var_usages_scan(code, indexStack + [k], varUsageDict, usageType)
                    elif usageType == 'set':
                        if ('var' in k) or ('code' in k) or ('else' in k):
                            varUsageDict = get_var_usages_scan(code, indexStack + [k], varUsageDict, usageType)
                    elif usageType == 'get':
                        if ('expression' in k) or ('condition' in k) or ('args' in k):
                            varUsageDict = get_var_usages_scan(code, indexStack + [k], varUsageDict, usageType)
                    i+=1
            elif type(block) == list:
                i = 0
                while i < len(block):
                    varUsageDict = get_var_usages_scan(code, indexStack + [i], varUsageDict, usageType)
                    i += 1
            else:
                if VariableNameManager.isValidVarName(block):
                    if not block in varUsageDict:
                        varUsageDict[block] = []
                    varType = 'get'
                    if indexStack[len(indexStack)-1] == 'var':
                        varType = 'set'
                    varUsageDict[block].append({'type': varType, 'stack': copy(indexStack)})
            return varUsageDict
        return get_var_usages_scan(code, [], {}, usageType)
    
    @staticmethod
    def add_line_paths(code):
        def add_line_paths_scan(code, indexStack):
            block = OptimizerUtil.follow_index_stack(code, indexStack)
            if type(block) == dict:
                block['line_path'] = copy(indexStack)
                i = 0
                while i < len(block.keys()):
                    k = list(block.keys())[i]
                    if ('code' in k) or ('else' in k):
                        code = add_line_paths_scan(code, indexStack + [k])
                    i+=1
            elif type(block) == list:
                i = 0
                while i < len(block):
                    varUsageDict = add_line_paths_scan(code, indexStack + [i])
                    i += 1
            return code
        return add_line_paths_scan(code, [])