import json
from codeSpliter import CodeSpliter
from optimizer import Optimizer
from piecer import Piecer
from assemblyBuilder import AssemblyBuilder

if __name__ == "__main__":
    import main

class Compiler:
    """used to compile code into assembly code"""

    @staticmethod
    def compile(inputCode):
        """
        Compiles code into assembly.\n
        Input a string containing all the code that you want to compile.
        """
        code = CodeSpliter.split(inputCode)
        piecedCode = Piecer.piece(code)
        optimizedPiecedCode = Optimizer.optimize_code(piecedCode)
        print('optimizedPiecedCode:', json.dumps(optimizedPiecedCode, indent=4))
        assemblyCode = AssemblyBuilder.make_assembly(optimizedPiecedCode)
        print('assemblyCode:', json.dumps(assemblyCode, indent=4))
        return assemblyCode