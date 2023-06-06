import json

if __name__ == "__main__":
    import main

class GPUCompiler:
    @staticmethod
    def runCompiler(code):
        print('before:', code)
        commands = GPUCompiler.replace_symbols(code)
        GPUCompiler.send_to_SM(GPUCompiler.encode(commands, 12))

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
        '>': 8,
        '=': 9,
        'get id':10,
        'id': 10,
        'input': 11,
        'in': 11,
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
                    command = GPUCompiler.replaceSymbolsMap[command]
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
                if command[1] < 0:
                    if command[0] == 0:
                        data = -(abs(command[1]) * encodingNumber)
                    else:
                        data = -((encodingNumber-command[0]) + abs(command[1]+1) * encodingNumber)
                else:
                    data = command[0] + abs(command[1]) * encodingNumber
                numberCommands.append(data)
            else:
                numberCommands.append(command)
        print(numberCommands)
        return numberCommands

    @staticmethod
    def send_to_SM(numberCommands: list[int]):
        with open("C:\Program Files (x86)\Steam\steamapps\common\Scrap Mechanic\Data\Importer\Importer.json", "w") as out_file:
            json.dump(numberCommands, out_file, indent = 4)