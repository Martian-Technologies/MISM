import json
from gpuCompiler import GPUCompiler
from gpuEmulator import GPU
import os
import sys


def run():
    """runs all the code"""
    
    # compiler + assembler
    filename = 'GPUcode.json'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    filename = r"GPU\\" + filename

    if not os.path.exists(filename):
        print(f'Error: file "{filename}" not found')
        exit(1)

    with open(filename, 'r') as f:
        data = json.load(f)
    
    commands = GPUCompiler.replace_symbols(data)
    numberCommands = GPUCompiler.encode(commands, 12)
    GPUCompiler.send_to_SM(numberCommands)

    # emulator
    gpu = GPU()
    gpu.run(numberCommands)

run()