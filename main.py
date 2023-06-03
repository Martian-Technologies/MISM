import json
import sys
import os
from assembler import Assembler
from emulator import Emulator
from compiler import Compiler

def run():
    """runs all the code"""
    
    # compiler + assembler
    filename = 'test.itc'
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    if not os.path.exists(filename):
        print(f'Error: file "{filename}" not found')
        exit(1)

    with open(filename, 'r') as f:
        code = Compiler.compile(f.read())
        code = Assembler.run(code, doPrints = False)
        Emulator.run(code)


    # assembler
    """
    fileName = 'test.mas'
    
    if len(sys.argv) > 1:
        fileName = sys.argv[1]

    if not os.path.exists(fileName):
        print(f'Error: file "{fileName}" not found')
        exit(1)

    code = []
    with open(fileName, 'r') as f:
        code = Assembler.run(f.readlines(), doPrints = False)

    Emulator.run(code)
    """

run()