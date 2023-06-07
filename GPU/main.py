import json
from gpuCompiler import GPUCompiler
from gpuEmulator import GPUemulator
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
    numberCommands = GPUCompiler.encode(commands, 24)
    GPUCompiler.send_to_SM(numberCommands)

    #emulator
    screen = GPUemulator.Screen(24, 16)
    gpu = GPUemulator.GPU(1)
    gpu.run(numberCommands, screen, layout=(1, 1))
    screen.display()

run()