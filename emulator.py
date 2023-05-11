import sys
import os
import operator
from assembler import Assembler

Assembler.run(doPrints = False)

PAUSE = False
DEBUG = False

filename = 'test.num.json'
if len(sys.argv) > 1:
    filename = sys.argv[1]

if not os.path.exists(filename):
    print(f'Error: file "{filename}" not found')
    exit(1)

import json

with open(filename, 'r') as f:
    code = json.load(f)

exec_pos = 0
memory = []
def set_memory(addr, val):
    global memory
    if addr >= len(memory):
        memory += [0] * (addr - len(memory) + 1)
    memory[addr] = val
    (input(memory) if PAUSE else print(memory)) if DEBUG else None

def get_memory(addr):
    global memory
    if addr >= len(memory):
        memory += [0] * (addr - len(memory) + 1)
    return memory[addr]

def get_code():
    global code, exec_pos
    if exec_pos >= len(code):
        return 0
    exec_pos += 1
    return code[exec_pos-1]

opcodes = [
    'HALT',
    'NOP',
    'SET',
    'OPR',
    'OPRCONST',
    'JUMP',
    'RAMJUMP',
    'JUMPIF',
    'MOV',
    'RMOV',
    'MOVR',
    'RMOVR',
    'PRI',
    'PRIA'
]

commands = []
while True:
    cmd_start_index = exec_pos
    cmd = get_code()
    opcode = opcodes[cmd]
    #print(opcode, code[exec_pos], code[exec_pos + 1], code[exec_pos + 2], code[exec_pos + 3])
    #print(memory)
    #input()

    if opcode == 'HALT':
        print('Halting...')
        break

    elif opcode == 'NOP':
        continue

    elif opcode == 'SET':
        addr = get_code()
        val = get_code()
        set_memory(addr, val)

    elif opcode == 'OPR':
        mode = [operator.add, operator.sub, operator.mul, operator.truediv, operator.mod, operator.pow][get_code()]
        read_addr1 = get_code()
        read_addr2 = get_code()
        write_addr = get_code()
        val1 = get_memory(read_addr1)
        val2 = get_memory(read_addr2)
        set_memory(write_addr, mode(val1, val2))

    elif opcode == 'OPRCONST':
        mode = [operator.add, operator.sub, operator.mul, operator.truediv, operator.mod, operator.pow][get_code()]
        read_addr = get_code()
        const = get_code()
        write_addr = get_code()
        val = get_memory(read_addr)
        set_memory(write_addr, mode(val, const))
    
    elif opcode == 'JUMP':
        mode = ['NORM', 'REL'][get_code()]
        value = get_code()
        if mode == 'NORM':
            exec_pos = value
        elif mode == 'REL':
            exec_pos = cmd_start_index + value
    
    elif opcode == 'RAMJUMP':
        mode = ['NORM', 'REL'][get_code()]
        read_addr = get_code()
        if mode == 'NORM':
            exec_pos = get_memory(read_addr)
        elif mode == 'REL':
            exec_pos = cmd_start_index + get_memory(read_addr)
    
    elif opcode == 'JUMPIF':
        operation = [operator.eq, operator.ne, operator.lt, operator.le][get_code()]
        read_addr1 = get_code()
        read_addr2 = get_code()
        jump_delta = get_code()
        val1 = get_memory(read_addr1)
        val2 = get_memory(read_addr2)
        if operation(val1, val2):
            exec_pos = cmd_start_index + jump_delta
        
    elif opcode == 'MOV':
        read_addr = get_code()
        write_addr = get_code()
        set_memory(write_addr, get_memory(read_addr))
    
    elif opcode == 'RMOV':
        read_addr = get_code()
        write_addr = get_code()
        read_addr = get_memory(read_addr)
        set_memory(write_addr, get_memory(read_addr))
    
    elif opcode == 'MOVR':
        read_addr = get_code()
        write_addr = get_code()
        write_addr = get_memory(write_addr)
        set_memory(write_addr, get_memory(read_addr))

    elif opcode == 'RMOVR':
        read_addr = get_code()
        write_addr = get_code()
        read_addr = get_memory(read_addr)
        write_addr = get_memory(write_addr)
        set_memory(write_addr, get_memory(read_addr))
    
    elif opcode == 'PRI':
        print(f'> {get_code()}') if not PAUSE else input(f'> {get_code()}')
    
    elif opcode == 'PRIA':
        print(f'> {get_memory(get_code())}') if not PAUSE else input(f'> {get_memory(get_code())}')