import json
from optimizerUtil import OptimizerUtil
from varNameManager import VariableNameManager

if __name__ == "__main__":
    import main

class Optimizer:
    @staticmethod
    def optimize_code(code):
        code = OptimizerUtil.add_line_paths(code)
        print('PiecedCode:', json.dumps(code, indent=4))
        for func in Optimizer.optimizeFunction:
            code = OptimizerUtil.add_line_paths(code)
            varUsages = OptimizerUtil.get_var_usages(code)
            code = func(code, varUsages)
        return code

    # you should rename this and name it the the type of optimization happening in it
    # also should have many for difrent types of optimization
    @staticmethod
    def optimize_code_function(code:list, varUsages:dict): 
        return code
    
    optimizeFunction = [
        optimize_code_function,
    ]