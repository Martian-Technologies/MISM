from __future__ import annotations
import math
if __name__ == "__main__":
    import main

class GPUemulator:
    class Screen(object):
        def __init__(self, x_size, y_size):
            self.x_size = x_size
            self.y_size = y_size
            self.screen = [[False for _ in range(x_size)] for _ in range(y_size)]
        def set(self, x, y, value):
            self.screen[y][x] = value
        def display(self):
            for row in self.screen:
                for value in row:
                    print('██' if value else '  ', end='')
                print()
            print()

    class Core(object):
        def __init__(self):
            self.memory = {}
            self.register = 0
        def run(self, instruction: str, argument: int):
            if instruction == 'r>':
                self.register = self.memory.get(argument, 0)
            elif instruction == 'r<':
                self.memory[argument] = self.register
            elif instruction == '+':
                self.register += self.memory.get(argument, 0)
            elif instruction == '-':
                self.register -= self.memory.get(argument, 0)
            elif instruction == '*':
                self.register *= self.memory.get(argument, 0)
            elif instruction == '/':
                self.register /= self.memory.get(argument, 0)
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
                raise Exception('GET should be replaced by IN <value> in GPU.run')
            elif instruction == 'x':
                raise Exception('X should be replaced by IN <value> in GPU.run')
            elif instruction == 'y':
                raise Exception('Y should be replaced by IN <value> in GPU.run')

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
                    core = self.cores[y_ind * layout[0] + x_ind]
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
                        if instruction == 'get':
                            instruction = 'in'
                            argument = ROM[argument] if argument > 0 and argument < len(ROM) and argument%1==0 else 0
                        elif instruction == 'x':
                            instruction = 'in'
                            argument = x * 100
                            # print('x', x)
                        elif instruction == 'y':
                            instruction = 'in'
                            argument = y * 100
                            # print('y', y)
                        core.run(instruction, argument)
                    # print(core.register)
                    screen.set(x, y, core.register > 0)