from pathlib import Path
import sys
import os
import operator
from assembler import Assembler

if __name__ == "__main__":
    import main

class Emulator:
    PAUSE = False
    DEBUG = False

    code = []
    exec_pos = 0
    memory = []
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

    @staticmethod
    def set_memory(addr, val):
        Emulator.memory
        if addr >= len(Emulator.memory):
            Emulator.memory += [0] * (addr - len(Emulator.memory) + 1)
        Emulator.memory[addr] = val
        (input(Emulator.memory) if Emulator.PAUSE else print(Emulator.memory)) if Emulator.DEBUG else None

    @staticmethod
    def get_memory(addr):
        Emulator.memory
        if addr >= len(Emulator.memory):
            Emulator.memory += [0] * (addr - len(Emulator.memory) + 1)
        return Emulator.memory[addr]

    @staticmethod
    def get_code():
        Emulator.code, Emulator.exec_pos
        if Emulator.exec_pos >= len(Emulator.code):
            return 0
        Emulator.exec_pos += 1
        return Emulator.code[Emulator.exec_pos-1]

    @staticmethod
    def run(code):
        Emulator.code = code
        while True:
            cmd_start_index = Emulator.exec_pos
            cmd = Emulator.get_code()
            opcode = Emulator.opcodes[cmd]
            #print(opcode, Emulator.code[exec_pos], Emulator.code[exec_pos + 1], Emulator.code[exec_pos + 2], Emulator.code[exec_pos + 3])
            #print(Emulator.memory)
            #input()
            if opcode == 'HALT':
                print('Halting...')
                break

            elif opcode == 'NOP':
                continue

            elif opcode == 'SET':
                addr = Emulator.get_code()
                val = Emulator.get_code()
                Emulator.set_memory(addr, val)

            elif opcode == 'OPR':
                mode = [operator.add, operator.sub, operator.mul, operator.truediv, operator.mod, operator.pow][Emulator.get_code()]
                read_addr1 = Emulator.get_code()
                read_addr2 = Emulator.get_code()
                write_addr = Emulator.get_code()
                val1 = Emulator.get_memory(read_addr1)
                val2 = Emulator.get_memory(read_addr2)
                Emulator.set_memory(write_addr, mode(val1, val2))

            elif opcode == 'OPRCONST':
                mode = [operator.add, operator.sub, operator.mul, operator.truediv, operator.mod, operator.pow][Emulator.get_code()]
                read_addr = Emulator.get_code()
                const = Emulator.get_code()
                write_addr = Emulator.get_code()
                val = Emulator.get_memory(read_addr)
                Emulator.set_memory(write_addr, mode(val, const))
            
            elif opcode == 'JUMP':
                mode = ['NORM', 'REL'][Emulator.get_code()]
                value = Emulator.get_code()
                if mode == 'NORM':
                    Emulator.exec_pos = value
                elif mode == 'REL':
                    Emulator.exec_pos = cmd_start_index + value
            
            elif opcode == 'RAMJUMP':
                mode = ['NORM', 'REL'][Emulator.get_code()]
                read_addr = Emulator.get_code()
                if mode == 'NORM':
                    Emulator.exec_pos = Emulator.get_memory(read_addr)
                elif mode == 'REL':
                    Emulator.exec_pos = cmd_start_index + Emulator.get_memory(read_addr)
            
            elif opcode == 'JUMPIF':
                operation = [operator.eq, operator.ne, operator.lt, operator.le][Emulator.get_code()]
                read_addr1 = Emulator.get_code()
                read_addr2 = Emulator.get_code()
                jump_delta = Emulator.get_code()
                val1 = Emulator.get_memory(read_addr1)
                val2 = Emulator.get_memory(read_addr2)
                if operation(val1, val2):
                    Emulator.exec_pos = cmd_start_index + jump_delta
                
            elif opcode == 'MOV':
                read_addr = Emulator.get_code()
                write_addr = Emulator.get_code()
                Emulator.set_memory(write_addr, Emulator.get_memory(read_addr))
            
            elif opcode == 'RMOV':
                read_addr = Emulator.get_code()
                write_addr = Emulator.get_code()
                read_addr = Emulator.get_memory(read_addr)
                Emulator.set_memory(write_addr, Emulator.get_memory(read_addr))
            
            elif opcode == 'MOVR':
                read_addr = Emulator.get_code()
                write_addr = Emulator.get_code()
                write_addr = Emulator.get_memory(write_addr)
                Emulator.set_memory(write_addr, Emulator.get_memory(read_addr))

            elif opcode == 'RMOVR':
                read_addr = Emulator.get_code()
                write_addr = Emulator.get_code()
                read_addr = Emulator.get_memory(read_addr)
                write_addr = Emulator.get_memory(write_addr)
                Emulator.set_memory(write_addr, Emulator.get_memory(read_addr))
            
            elif opcode == 'PRI':
                print(f'> {Emulator.get_code()}') if not Emulator.PAUSE else input(f'> {Emulator.get_code()}')
            
            elif opcode == 'PRIA':
                print(f'> {Emulator.get_memory(Emulator.get_code())}') if not Emulator.PAUSE else input(f'> {Emulator.get_memory(Emulator.get_code())}')