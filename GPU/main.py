import json
from gpuCompiler import GPUCompiler
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
        
        GPUCompiler.runCompiler(json.JSONDecoder().decode(f.read()))

run()