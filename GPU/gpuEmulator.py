if __name__ == "__main__":
    import main

import math
class GPUemulator:
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
                self.register %= self.memory.get(argument, 0)
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
                ...


    class GPU(object):
        def __init__(self, cores: int):
            self.cores: list[GPUemulator.Core] = []
            for i in range(cores):
                self.cores.append(GPUemulator.Core())

        def run(self, commands: list[int], start: int, length: int, repeat: bool, layout: tuple[int, int]):
            for command in commands:
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
                print(instruction, argument)
