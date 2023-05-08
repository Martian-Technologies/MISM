import sys
import os

PAUSE = True
DEBUG = True

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
    'NOP',
    'SET',
    'OPR',
    'ONC',
    'JMP',
    'JMI',
    'HALT',
    'PRNT',
    'PRTA',
    'GMP',
    'GMA',
    'MOV'
]

while True:
    opcode = get_code()
    opcode = opcodes[opcode] if opcode < len(opcodes) else opcode
    if opcode == 'NOP':
        continue
    elif opcode == 'SET':
        addr = get_code()
        val = get_code()
        set_memory(addr, val)
    elif opcode == 'OPR':
        operation = get_code()
        addr1 = get_code()
        addr2 = get_code()
        addr3 = get_code()
        if operation == 0:
            set_memory(addr3, get_memory(addr1) + get_memory(addr2))
        elif operation == 1:
            set_memory(addr3, get_memory(addr1) - get_memory(addr2))
        elif operation == 2:
            set_memory(addr3, get_memory(addr1) * get_memory(addr2))
        elif operation == 3:
            set_memory(addr3, get_memory(addr1) / get_memory(addr2))
        elif operation == 4:
            set_memory(addr3, get_memory(addr1) % get_memory(addr2))
        else:
            print(f'Error: invalid operation "{operation}"')
            exit(1)
    elif opcode == 'ONC':
        operation = get_code()
        addr1 = get_code()
        value = get_code()
        addr2 = get_code()
        if operation == 0:
            set_memory(addr2, get_memory(addr1) + value)
        elif operation == 1:
            set_memory(addr2, get_memory(addr1) - value)
        elif operation == 2:
            set_memory(addr2, get_memory(addr1) * value)
        elif operation == 3:
            set_memory(addr2, get_memory(addr1) / value)
        elif operation == 4:
            set_memory(addr2, get_memory(addr1) % value)
        elif operation == 5:
            set_memory(addr2, value - get_memory(addr1))
        elif operation == 6:
            set_memory(addr2, value / get_memory(addr1))
        elif operation == 7:
            set_memory(addr2, value % get_memory(addr1))
        else:
            print(f'Error: invalid operation "{operation}"')
            exit(1)
    elif opcode == 'JMP':
        delta = get_code()
        exec_pos += delta
    elif opcode == 'JMI':
        operation = get_code()
        addr1 = get_code()
        addr2 = get_code()
        delta = get_code()
        if operation == 0:
            if get_memory(addr1) == get_memory(addr2):
                exec_pos += delta
        elif operation == 1:
            if get_memory(addr1) != get_memory(addr2):
                exec_pos += delta
        elif operation == 2:
            if get_memory(addr1) < get_memory(addr2):
                exec_pos += delta
        elif operation == 3:
            if get_memory(addr1) <= get_memory(addr2):
                exec_pos += delta
        else:
            print(f'Error: invalid operation "{operation}"')
            exit(1)
    elif opcode == 'HALT':
        print('Halting...')
        break
    elif opcode == 'PRNT':
        value = get_code()
        (input(f'> {value}') if PAUSE else print(f'> {value}')) if DEBUG else None
    elif opcode == 'PRTA':
        addr = get_code()
        (input(f'> {get_memory(addr)}') if PAUSE else print(f'> {get_memory(addr)}')) if DEBUG else None
    elif opcode == 'GMP':
        addr = get_code()
        exec_pos = addr
    elif opcode == 'GMA':
        addr = get_code()
        exec_pos = get_memory(addr)
    elif opcode == 'MOV':
        addr1 = get_code()
        addr2 = get_code()
        set_memory(addr2, get_memory(addr1))
    else:
        print(f'Error: invalid opcode "{opcode}"')
        exit(1)
