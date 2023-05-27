import json
from codeSpliter import CodeSpliter
from codeTranslate import CodePiecer

class Compiler:
    """used to compile code into assembly code"""

    reserved = {
        'if': 'IF',
        'then': 'THEN',
        'else': 'ELSE',
        'while': 'WHILE',
        'do': 'DO',
        'end': 'END',
        'print': 'PRINT',
        'for': 'FOR'
    }

    """
    Please use functions to make code easier to read.
    You have a horibal habit to make all the code in one giant block.
    Please make helper functions. You should have a ton, you have one.
    """

    @staticmethod
    def compile(inputCode):
        """
        Compiles code into assembly.\n
        Input a string containing all the code that you want to compile.
        """
        code = CodeSpliter.split(inputCode)
        translatedCode = CodePiecer.piece(code)
        return translatedCode
        #return piecedCode
