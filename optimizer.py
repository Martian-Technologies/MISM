import json
from stackUtil import StackUtil
from varNameManager import VariableNameManager

if __name__ == "__main__":
    import main

class Optimizer:
    @staticmethod
    def optimize_code(code):
        code = StackUtil.add_line_paths(code)
        print('optimize_code input', json.dumps(code, indent=4))
        for func in Optimizer.optimizeFunction:
            code = StackUtil.add_line_paths(code)
            varUsages = StackUtil.get_var_usages(code)
            code = func(code, varUsages)
        code = StackUtil.add_line_paths(code)
        return code

    # you should rename this and name it the the type of optimization happening in it
    # also should have many for difrent types of optimization
    @staticmethod
    def optimize_code_function(code:list, varUsages:dict): 
        return code

    @staticmethod
    def remove_extra_defines(code:list, varUsages:dict):
        for var in varUsages:
            i = 0
            for path in varUsages[var]:
                if path['type'] == 'define':
                    if i != 0:
                        code = StackUtil.remove_command(code, path['stack'])
                        varUsages = StackUtil.get_var_usages(code)
                        return Optimizer.remove_extra_defines(code, varUsages)
                i+=1
        return code
    
    optimizeFunction = [
        remove_extra_defines,
    ]