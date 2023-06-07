import json

if __name__ == "__main__":
    import main

class GPUJumper:
    @staticmethod
    def run_compiler(code):
        """ The input of this is the out put of GPUCompiler """
        print('code:', code)
        commands = [
            [3, 0],
            [2, 0],
            ]
        blockTime = GPUJumper.get_block_time(code) - GPUJumper.get_commands_time_till_next_command(commands)
        waitTime = blockTime - 5
        commands.append([1, waitTime])
        commands.append([3, 2])
        commands.append([0, 0])
        GPUJumper.send_to_SM(GPUJumper.encode(commands, 8))
    
    @staticmethod
    def encode(commands: list, encodingNumber: int):
        print('after:', commands)
        numberCommands:list = []
        for command in commands:
            if type(command) == list:
                data = None
                if len(command) == 1:
                    data = command[0]
                else:
                    data = command[0] + abs(command[1]) * encodingNumber
                numberCommands.append(data)
            else:
                numberCommands.append(command)
        print(numberCommands)
        return numberCommands
    
    @staticmethod
    def get_block_time(block):
        lenght = len(block)
        return lenght * 3
 
    @staticmethod
    def send_to_SM(numberCommands: list[int]):
        print("Import now")
        with open("C:\Program Files (x86)\Steam\steamapps\common\Scrap Mechanic\Data\Importer\Importer.json", "w") as out_file:
            json.dump(numberCommands, out_file, indent = 4)
        print("Press enter when imported")
        input()

    @staticmethod
    def get_command_time_till_next_command(command):
        commandTimes = {
            0: "THE CODE HAS ENDED",
            1: 5,
            2: 6,
            3: 6
        }
        time = commandTimes[command[0]]
        if command[0] == 1:
            if command[1] < 1:
                command[1] = 1
            time += command[1]
        return time
    
    @staticmethod
    def get_command_time_till_applied_on_gpu(command):
        commandTimes = {
            0: "THE CODE HAS ENDED",
            1: 0,
            2: 3,
            3: 9
        }
        return commandTimes[command]
    
    @staticmethod
    def get_commands_time_till_next_command(commands):
        time = 0
        for command in commands:
            time += GPUJumper.get_command_time_till_next_command(command)
        return time
        
        