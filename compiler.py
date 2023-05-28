import json
from codeSpliter import CodeSpliter
from piecer import Piecer

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
        print('piecedCode:', json.dumps(piecedCode, indent=4))
        return