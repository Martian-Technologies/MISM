import json
from math import floor

if __name__ == "__main__":
    import main

class GPUCompiler:
    @staticmethod
    def run_compiler(code):
        print('before:', code)
        commands = GPUCompiler.replace_symbols(code)
        GPUCompiler.send_to_SM(commands, 24)

    replaceSymbolsMap = {
        'r>': 0,
        'r<': 1,
        '+': 2,
        '-': 3,
        '*': 4,
        '/': 5,
        '%': 6,
        'sqrt': 7,
        'sq': 7,
        'floor': 8,
        'f': 8,
        'max': 9,
        'm': 9,
        '>': 10,
        '=': 11,
        'input': 12,
        'in': 12,
        'computer input': 13,
        'cin': 13,
        'get data': 14,
        'get': 14,
        'get x': 15,
        'x': 15,
        'get y': 16,
        'y': 16
    }
    
    @staticmethod
    def replace_symbols(code):
        commands = []
        for command in code:
            if type(command) == list:
                newCommand = []
                for item in command:
                    if type(item) == str:
                        item = item.lower()
                    if item in GPUCompiler.replaceSymbolsMap:
                        item = GPUCompiler.replaceSymbolsMap[item]
                    if type(item) == str:
                        raise Exception(f"could not find symbol {item}")
                    newCommand.append(item)
                if len(newCommand) == 1:
                    newCommand = newCommand[0]
                elif len(newCommand) != 2:
                    raise Exception(f"could not find command {command}")
            else:
                newCommand = None
                if type(command) == str:
                    command = command.lower()
                if command in GPUCompiler.replaceSymbolsMap:
                    newCommand = GPUCompiler.replaceSymbolsMap[command]
            commands.append(newCommand) 
        return commands

    @staticmethod
    def encode(commands: list, encodingNumber: int):
        print('after:', commands)
        print('length:', len(commands))
        numberCommands:list = []
        for command in commands:
            if type(command) == list:
                data = None
                dec = 1
                if command[0] == GPUCompiler.replaceSymbolsMap['input']:
                    dec = 100
                if command[1] < 0:
                    if command[0] == 0:
                        data = -(floor(abs(command[1]) * dec) * encodingNumber)
                    else:
                        data = -(encodingNumber-command[0] + floor(abs(command[1]) * dec) * encodingNumber)
                else:
                    data = command[0] + floor(abs(command[1]) * dec) * encodingNumber
                numberCommands.append(data)
            else:
                numberCommands.append(command)
        print(numberCommands)
        return numberCommands

    @staticmethod
    def send_to_SM(numberCommands: list[int]):
        print("Import now")
        with open("C:\Program Files (x86)\Steam\steamapps\common\Scrap Mechanic\Data\Importer\Importer.json", "w") as out_file:
            json.dump(numberCommands, out_file, indent = 4)
        print("Press enter when imported")
        input()