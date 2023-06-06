if __name__ == "__main__":
    import main

class Core(object):
    def __init__(self):
        self.memory = []
        self.register = 0
    def run(self, instruction: str, argument: int):
        if 

class GPU(object):
    def __init__(self, cores: int):
        self.cores: list[Core] = []
        for i in range(cores):
            self.cores.append(Core())

    def run(self, commands: list[int], start: int, length: int, repeat: bool, layout: tuple[int, int]):
        for command in commands:
            instruction = command % 12
            argument = command // 12
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
                '>',
                '=',
                'id',
                'in',
            ][instruction]
            print(instruction, argument)