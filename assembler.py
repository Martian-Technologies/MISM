import sys
import os
import json
from pathlib import Path

if __name__ == "__main__":
    import main

class Assembler:
    """used to assemble assembly into machine code"""
    WARNINGS = True

    opcodes = [
        'HALT',
        'NOP',
        'SET',
        'OPR',
        'ONC',
        'RJMP',
        'JMP',
        'RJMA',
        'JMA',
        'JMIF',
        'M',
        'RM',
        'MR',
        'RMR',
        'PRI',
        'PRIA',
        'RAW',
    ]

    alias_table = {
        'OPR': ['MATH'],
        'ONC': ['OPRC', 'CMATH'],
        'RJMA': ['RJMPA'],
        'JMA': ['JMPA'],
        'JMIF': ['JMPIF'],
        'M': ['MV', 'MOV'],
        'RM': ['RMV', 'RMOV'],
        'MR': ['MVR', 'MOVR'],
        'RMR': ['RMVR', 'RMOVR'],
        'add': ['+'],
        'sub': ['-'],
        'mul': ['*'],
        'div': ['/'],
        'mod': ['%'],
        'pow': ['^'],
        'rsub': ['r-'],
        'rdiv': ['r/'],
        'rmod': ['r%'],
        'rpow': ['r^'],
        'equ': ['='],
        'neq': ['!='],
        'lss': ['<'],
        'leq': ['<='],
        'mor': ['>'],
        'meq': ['>='],
    }

    replacements = {}

    definitions = {}
    all_labels = {}

    cmd_start_index = 0
    
    doDumps = True
    doPrints = True

    @staticmethod
    def init_static():
        if '--no-warn' in sys.argv:
            Assembler.WARNINGS = False

        for opcode in Assembler.alias_table:
            for alias in Assembler.alias_table[opcode]:
                Assembler.replacements[alias.lower()] = opcode
            Assembler.replacements[opcode] = opcode
        for opcode in Assembler.opcodes:
            Assembler.replacements[opcode.lower()] = opcode

    @staticmethod
    def error(msg):
        print(f'Error: {msg}')
        exit(1)

    @staticmethod
    def warn(msg):
        if not Assembler.WARNINGS:
            return
        print(f'Warning: {msg}')

    @staticmethod
    def parse_value(value, line):
        if value.startswith('@') and value[1:] in Assembler.definitions:
            return value
        if (value.startswith('!') or value.startswith('~')) and value[1:] in Assembler.all_labels:
            return value
        try:
            return int(value) if value.isdigit() else float(value)
        except ValueError:
            Assembler.error(f'invalid value "{value}" on line {line["line"]}')

    @staticmethod
    def print_pass(lines):
        print('\n')
        for line in lines:
            print(f'{line["line"]:3} | {line["content"]}')

    @staticmethod
    def smart_parse(value, line):
        if type(value) in [int, float]:
            return value
        if value.startswith('!'):
            label = Assembler.all_labels[value[1:]]
            return label
        if value.startswith('~'):
            label = Assembler.all_labels[value[1:]]
            return label - Assembler.cmd_start_index
        if value.startswith('@'):
            return Assembler.smart_parse(Assembler.definitions[value[1:]], line)
        try:
            return int(value) if value.isdigit() else float(value)
        except ValueError:
            Assembler.error(f'invalid value "{value}" on line {line["line"]}')

    @staticmethod
    def run(assembly_code, doDumps = True, doPrints = True):
        """ runs the assembler """ 
        Assembler.doDumps = doDumps
        Assembler.doPrints = doPrints
        Assembler.definitions = {}
        Assembler.all_labels = {}
    
        pass1 = []
        for i, line in enumerate(assembly_code):
            code = line.split('#')[0].strip()
            if code == '':
                continue
            pass1.append({'line': i+1, 'content': code})
        if Assembler.doPrints:
            Assembler.print_pass(pass1)
        pass2 = []
        for line in pass1:
            if line['content'].startswith('@'):
                tokens = line['content'].split()
                if len(tokens) != 3:
                    Assembler.error(f'invalid definition "{line["content"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')
                if tokens[1] in Assembler.definitions:
                    Assembler.error(f'duplicate definition "{line["content"]}" on line {line["line"]}. "{tokens[1]}" is already defined.')
                Assembler.definitions[tokens[1]] = tokens[2]
            else:
                pass2.append(line)
        if len(pass2) > 0:
            if pass2[-1]['content'] != 'HALT':
                pass2.append({'line': len(pass2)+1, 'content': 'HALT'})
        else:
            pass2.append({'line': 1, 'content': 'HALT'})

        if Assembler.doPrints:
            Assembler.print_pass(pass2)

        pass3 = []
        label_track = []
        for line in pass2:
            content = line['content']
            if content.endswith(':'):
                if ' ' in content:
                    Assembler.error(f'invalid label "{content}". Label cannot contain spaces.')
                if content[:-1] in Assembler.all_labels:
                    Assembler.error(f'duplicate label "{content}" on line {line["line"]}. "{content[:-1]}" is already defined.')
                label_track.append(content[:-1])
                Assembler.all_labels[content[:-1]] = None
                continue
            else:
                pass3.append({
                    'line': line['line'],
                    'content': {'tokens': content.split(), 'labels': label_track},
                    'og': line['content']
                })
                label_track = []
        
        if Assembler.doPrints:
            Assembler.print_pass(pass3)

        pass4 = []
        for line in pass3:
            tokens = line['content']['tokens']
            labels = line['content']['labels']
            for label in labels:
                Assembler.all_labels[label] = sum([len(x['content']) for x in pass4])
            if Assembler.replacements[tokens[0].lower()] == 'HALT':
                if len(tokens) != 1:
                    Assembler.error(f'invalid HALT instruction "{line["og"]}" on line {line["line"]}. Expected 1 tokens, got {len(tokens)}.')
                pass4.append({'line': line['line'], 'content': [0]})

            elif Assembler.replacements[tokens[0].lower()] == 'NOP':
                if len(tokens) != 1:
                    Assembler.error(f'invalid NOP instruction "{line["og"]}" on line {line["line"]}. Expected 1 tokens, got {len(tokens)}.')
                pass4.append({'line': line['line'], 'content': [1]})

            elif Assembler.replacements[tokens[0].lower()] == 'SET':
                if len(tokens) != 3:
                    Assembler.error(f'invalid SET instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

                addr = Assembler.parse_value(tokens[1], line)
                value = Assembler.parse_value(tokens[2], line)

                pass4.append({'line': line['line'], 'content': [2, addr, value]})

            elif Assembler.replacements[tokens[0].lower()] == 'OPR':
                if len(tokens) != 5:
                    Assembler.error(f'invalid OPR instruction "{line["og"]}" on line {line["line"]}. Expected 5 tokens, got {len(tokens)}.')

                opetaion_options = [
                    'add',
                    'sub',
                    'mul',
                    'div',
                    'mod',
                    'pow',
                ]
                operation = tokens[1].lower()
                if operation not in Assembler.replacements:
                    Assembler.error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
                operation = Assembler.replacements[operation]

                if operation not in opetaion_options:
                    Assembler.error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
                operation = opetaion_options.index(operation.lower())
                addr1 = Assembler.parse_value(tokens[2], line)
                addr2 = Assembler.parse_value(tokens[3], line)
                addr3 = Assembler.parse_value(tokens[4], line)

                pass4.append({'line': line['line'], 'content': [3, operation, addr1, addr2, addr3]})

            elif Assembler.replacements[tokens[0].lower()] == 'ONC':
                if len(tokens) != 5:
                    Assembler.error(f'invalid ONC instruction "{line["og"]}" on line {line["line"]}. Expected 5 tokens, got {len(tokens)}.')
                opetaion_options = [
                    'add',
                    'sub',
                    'mul',
                    'div',
                    'mod',
                    'pow',
                ]
                operation = tokens[1].lower()
                if operation not in Assembler.replacements:
                    Assembler.error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
                operation = Assembler.replacements[operation]

                if operation not in opetaion_options:
                    Assembler.error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
                operation = opetaion_options.index(operation.lower())
                addr1 = Assembler.parse_value(tokens[2], line)
                addr2 = Assembler.parse_value(tokens[3], line)
                addr3 = Assembler.parse_value(tokens[4], line)

                pass4.append({'line': line['line'], 'content': [4, operation, addr1, addr2, addr3]})

            elif Assembler.replacements[tokens[0].lower()] == 'RJMP':
                if len(tokens) != 2:
                    Assembler.error(f'invalid RJMP instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

                delta = Assembler.parse_value(tokens[1], line)
                if type(delta) == str:
                    if delta.startswith('!'):
                        Assembler.warn(f'RJMP instruction uses relative addressing, but "{delta}" is an absolute address on line {line["line"]}.')

                pass4.append({'line': line['line'], 'content': [5, 1, delta]})

            elif Assembler.replacements[tokens[0].lower()] == 'JMP':
                if len(tokens) != 2:
                    Assembler.error(f'invalid JMP instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

                addr = Assembler.parse_value(tokens[1], line)
                if type(addr) == str:
                    if addr.startswith('~'):
                       Assembler.warn(f'JMP instruction uses absolute addressing, but "{addr}" is a relative address on line {line["line"]}.')

                pass4.append({'line': line['line'], 'content': [5, 0, addr]})

            elif Assembler.replacements[tokens[0].lower()] == 'RJMA':
                if len(tokens) != 2:
                    Assembler.error(f'invalid RJMA instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

                addr = Assembler.parse_value(tokens[1], line)
                if type(addr) == str:
                    if addr.startswith('!'):
                        Assembler.warn(f'RJMA instruction reads jump delta from RAM, but an absolute address "{addr}" was given on line {line["line"]}.')
                    if addr.startswith('~'):
                        Assembler.warn(f'RJMA instruction reads jump delta from RAM, but a relative address "{addr}" was given on line {line["line"]}.')

                pass4.append({'line': line['line'], 'content': [6, 1, addr]})

            elif Assembler.replacements[tokens[0].lower()] == 'JMA':
                if len(tokens) != 2:
                    Assembler.error(f'invalid JMA instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

                addr = Assembler.parse_value(tokens[1], line)
                if type(addr) == str:
                    if not addr.startswith('!'):
                        Assembler.warn(f'JMA instruction reads jump address from RAM, but an absolute address "{addr}" was given on line {line["line"]}.')
                    if not addr.startswith('~'):
                        Assembler.warn(f'JMA instruction reads jump address from RAM, but a relative address "{addr}" was given on line {line["line"]}.')

                pass4.append({'line': line['line'], 'content': [6, 0, addr]})

            elif Assembler.replacements[tokens[0].lower()] == 'JMIF':
                if len(tokens) != 5:
                    Assembler.error(f'invalid JMIF instruction "{line["og"]}" on line {line["line"]}. Expected 5 tokens, got {len(tokens)}.')
                opetaion_options = [
                    'equ',
                    'neq',
                    'lss',
                    'leq'
                ]
                flipOperation = {
                    'mor': 'lss',
                    'meq': 'leq',
                }
                operation = tokens[1].lower()
                if operation not in Assembler.replacements:
                    Assembler.error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
                operation = Assembler.replacements[operation]
                num1 = tokens[2]
                num2 = tokens[3]
                if operation in flipOperation:
                    num2 = tokens[2]
                    num1 = tokens[3]
                    operation = flipOperation[operation]
                if operation not in opetaion_options:
                    Assembler.error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
                operation = opetaion_options.index(operation.lower())
                addr1 = Assembler.parse_value(num1, line)
                addr2 = Assembler.parse_value(num2, line)
                delta = Assembler.parse_value(tokens[4], line)
                if type(addr) == str:
                    if addr.startswith('!'):
                        Assembler.warn(f'JMIF instruction uses relative addressing, but "{delta}" is an absolute address on line {line["line"]}.')

                pass4.append({'line': line['line'], 'content': [7, operation, addr1, addr2, delta]})

            elif Assembler.replacements[tokens[0].lower()] == 'M':
                if len(tokens) != 3:
                    Assembler.error(f'invalid M instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

                addr1 = Assembler.parse_value(tokens[1], line)
                addr2 = Assembler.parse_value(tokens[2], line)

                pass4.append({'line': line['line'], 'content': [8, addr1, addr2]})

            elif Assembler.replacements[tokens[0].lower()] == 'RM':
                if len(tokens) != 3:
                    Assembler.error(f'invalid RMV instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

                addr1 = Assembler.parse_value(tokens[1], line)
                addr2 = Assembler.parse_value(tokens[2], line)

                pass4.append({'line': line['line'], 'content': [9, addr1, addr2]})

            elif Assembler.replacements[tokens[0].lower()] == 'MR':
                if len(tokens) != 3:
                    Assembler.error(f'invalid RMV instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

                addr1 = Assembler.parse_value(tokens[1], line)
                addr2 = Assembler.parse_value(tokens[2], line)

                pass4.append({'line': line['line'], 'content': [10, addr1, addr2]})

            elif Assembler.replacements[tokens[0].lower()] == 'RMR':
                if len(tokens) != 3:
                    Assembler.error(f'invalid RMR instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

                addr1 = Assembler.parse_value(tokens[1], line)
                addr2 = Assembler.parse_value(tokens[2], line)

                pass4.append({'line': line['line'], 'content': [11, addr1, addr2]})

            elif Assembler.replacements[tokens[0].lower()] == 'PRI':
                if len(tokens) != 2:
                    Assembler.error(f'invalid PRI instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

                value = Assembler.parse_value(tokens[1], line)

                pass4.append({'line': line['line'], 'content': [12, value]})

            elif Assembler.replacements[tokens[0].lower()] == 'PRIA':
                if len(tokens) != 2:
                    Assembler.error(f'invalid PRIA instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

                addr = Assembler.parse_value(tokens[1], line)

                pass4.append({'line': line['line'], 'content': [13, addr]})
            
            elif Assembler.replacements[tokens[0].lower()] == 'RAW':
                if len(tokens) == 1:
                    Assembler.error(f'invalid RAW instruction "{line["og"]}" on line {line["line"]}. Expected at least 1 token, got {len(tokens)}.')
                content = []
                for token in tokens[1:]:
                    value = Assembler.parse_value(token, line)
                    content.append(value)
                pass4.append({'line': line['line'], 'content': content})
                
            else:
                Assembler.error(f'invalid instruction "{line["og"]}" on line {line["line"]}')

        if Assembler.doPrints:
            Assembler.print_pass(pass4)

        pass5 = []

        for line in pass4:
            # pass5.append('\n')
            Assembler.cmd_start_index = len(pass5)
            for cmd in line['content']:
                if type(cmd) != str:
                    pass5.append(cmd)
                    continue
                pass5.append(Assembler.smart_parse(cmd, line))

        # print(all_labels)

        print_thing = [[]]
        pass_4_index = 0
        pass_4_internal_index = 0
        for cmd in pass5:
            print_thing[-1].append(str(cmd))
            if pass_4_internal_index == len(pass4[pass_4_index]['content']) - 1:
                str_len = sum([len(x) for x in print_thing[-1]])+len(print_thing[-1])-1
                spaces = 14 - str_len
                print_thing[-1].append((' '*spaces)+' # '+str(' '.join(pass3[pass_4_index]['content']['tokens'])))
                pass_4_index += 1
                pass_4_internal_index = 0
                print_thing.append([])
            else:
                pass_4_internal_index += 1

        if Assembler.doPrints:
            print()
            print('\n'.join([' '.join(line) for line in print_thing]))

        if Assembler.doDumps:
            with open("C:\Program Files (x86)\Steam\steamapps\common\Scrap Mechanic\Data\Importer\Importer.json", "w") as out_file:
                json.dump(pass5, out_file, indent = 4)
        """
            dump_fileName = Path("machineCode/"+'.'.join(fileName.split('.')[:-1]+['num', 'json']))
            with open(dump_fileName, 'w') as out_file:
                json.dump(pass5, out_file, indent = 4)
        """
        return pass5

Assembler.init_static()