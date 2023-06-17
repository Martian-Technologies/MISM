from __future__ import annotations
import math
if __name__ == "__main__":
    import main
import json
class GPUemulator:
    class Screen(object):
        def __init__(self, x_size, y_size):
            self.x_size = x_size
            self.y_size = y_size
            self.screen = [[False for _ in range(x_size)] for _ in range(y_size)]
        def set(self, x, y, value):
            self.screen[y][x] = value
        def display(self):
            print('+'+'-'*self.x_size*2+'+')
            for row in self.screen:\
                print('|'+''.join('██' if value else '  ' for value in row)+'|')
            print('+'+'-'*self.x_size*2+'+')

    class Core(object):
        def __init__(self):
            self.memory = {}
            self.register = 0
            self.ROM = []
        def run(self, instruction: str, argument: int):
            if instruction == 'r>':
                self.register = self.memory.get(argument, 0)
            elif instruction == 'r<':
                self.memory[argument] = self.register
                self.register = 0
            elif instruction == '+':
                self.register += self.memory.get(argument, 0)
            elif instruction == '-':
                self.register -= self.memory.get(argument, 0)
            elif instruction == '*':
                self.register *= self.memory.get(argument, 0)
            elif instruction == '/':
                if self.memory.get(argument, 0) == 0:
                    self.register = 100000000
                else:
                    self.register = self.register / self.memory.get(argument, 0)
            elif instruction == '%':
                self.register = self.register % self.memory.get(argument, 0)
            elif instruction == 'sq':
                if self.memory.get(argument, 0) == 0:
                    raise Exception('cannot root 0')
                root_value = self.memory.get(argument, 0)
                if root_value == 0 and self.register == 1:
                    self.register = 1
                elif root_value == 0:
                    raise Exception('cannot root 0')
                elif root_value == 2:
                    self.register = math.sqrt(self.register)
                elif root_value == 3:
                    self.register = math.cbrt(self.register)
                else:
                    self.register = self.register ** (1 / root_value)
            elif instruction == 'f':
                self.register = math.floor(self.register)
            elif instruction == 'm':
                self.register = max(self.register, self.memory.get(argument, 0))
            elif instruction == '>':
                self.register = 1 if self.register > self.memory.get(argument, 0) else 0
            elif instruction == '=':
                self.register = 1 if self.register == self.memory.get(argument, 0) else 0
            elif instruction == 'in':
                self.register = argument / 100
            elif instruction == 'cin':
                # not implemented
                raise NotImplementedError('Command CIN not implemented')
            elif instruction == 'get':
                if self.register % 1 == 0 and self.register > 0 and self.register < len(self.ROM):
                    self.register = math.floor(self.register)
                    self.register = self.ROM[self.register]
                else:
                    self.register = 0
            elif instruction == 'x':
                raise Exception('X should be replaced by IN <value> in GPU.run')
            elif instruction == 'y':
                raise Exception('Y should be replaced by IN <value> in GPU.run')
            self.register = max(-3.2999999654827e+38, min(3.2999999654827e+38, self.register))

    class GPU(object):
        def __init__(self, cores: int):
            self.cores: list[GPUemulator.Core] = []
            for i in range(cores):
                self.cores.append(GPUemulator.Core())

        def run(self, commands: list[int], screen: GPUemulator.Screen, ROM: list[int] = [], layout: tuple[int, int] = (1, 1), start: int = 0, length: int|None = None):
            length = length if length is not None else len(commands)
            num_cores = len(self.cores)
            for y in range(screen.y_size):
                for x in range(screen.x_size):
                    x_ind = x % layout[0]
                    y_ind = y % layout[1]
                    # print(f'calculating pixel {x}, {y} on core {y_ind * layout[0] + x_ind}')
                    core:GPUemulator.Core = self.cores[y_ind * layout[0] + x_ind]
                    core.ROM = ROM
                    for command in commands[start:start+length]:
                        instruction = command % 24
                        argument = command // 24
                        # print(instruction, argument)
                        instruction = [
                            'r>',
                            'r<',
                            '+',
                            '-',
                            '*',
                            '/',
                            '%',
                            'sq',
                            'f',
                            'm',
                            '>',
                            '=',
                            'in',
                            'cin',
                            'get',
                            'x',
                            'y',
                        ][instruction]
                        # print(f'command: {instruction} {argument}')
                        if instruction == 'x':
                            instruction = 'in'
                            argument = x * 100
                            # print('x', x)
                        elif instruction == 'y':
                            instruction = 'in'
                            argument = y * 100
                            # print('y', y)
                        core.run(instruction, argument)
                    print(x, y, core.memory)
                    # mem_dump = []
                    # for addr in core.memory:
                    #     addr += 10
                    #     while len(mem_dump) <= addr:
                    #         mem_dump.append(0)
                    #     mem_dump[addr] = core.memory[addr-10]
                    # print(f'memory:\n{json.dumps(mem_dump)}')
                    # print()
                    # input()
                    screen.set(x, y, core.memory.get(commands[start:start+length][-1]// 24) > 0)