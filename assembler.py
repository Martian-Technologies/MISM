import sys
import os
import json


WARNINGS = True
if '--no-warn' in sys.argv:
    WARNINGS = False

filename = 'test.mas'
if len(sys.argv) > 1:
    filename = sys.argv[1]

def error(msg):
    print(f'Error: {msg}')
    exit(1)

def warn(msg):
    if not WARNINGS:
        return
    print(f'Warning: {msg}')

if not os.path.exists(filename):
    error(f'file "{filename}" not found')


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
for opcode in alias_table:
    for alias in alias_table[opcode]:
        replacements[alias.lower()] = opcode
    replacements[opcode] = opcode
for opcode in opcodes:
    replacements[opcode.lower()] = opcode

definitions = {}
all_labels = {}
def parse_value(value, line):
    if value.startswith('@') and value[1:] in definitions:
        return value
    if (value.startswith('!') or value.startswith('~')) and value[1:] in all_labels:
        return value
    try:
        return int(value) if value.isdigit() else float(value)
    except ValueError:
        error(f'invalid value "{value}" on line {line["line"]}')

def print_pass(lines):
    print('\n')
    for line in lines:
        print(f'{line["line"]:3} | {line["content"]}')

pass1 = []
with open(filename, 'r') as f:
    for i, line in enumerate(f.readlines()):
        code = line.split('#')[0].strip()
        if code == '':
            continue
        pass1.append({'line': i+1, 'content': code})

print_pass(pass1)

pass2 = []
for line in pass1:
    if line['content'].startswith('@'):
        tokens = line['content'].split()
        if len(tokens) != 3:
            error(f'invalid definition "{line["content"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')
        if tokens[1] in definitions:
            error(f'duplicate definition "{line["content"]}" on line {line["line"]}. "{tokens[1]}" is already defined.')
        definitions[tokens[1]] = tokens[2]
    else:
        pass2.append(line)

if pass2[-1]['content'] != 'HALT':
    pass2.append({'line': len(pass2)+1, 'content': 'HALT'})

print_pass(pass2)

pass3 = []
label_track = []
for line in pass2:
    content = line['content']
    if content.endswith(':'):
        if ' ' in content:
            error(f'invalid label "{content}". Label cannot contain spaces.')
        if content[:-1] in all_labels:
            error(f'duplicate label "{content}" on line {line["line"]}. "{content[:-1]}" is already defined.')
        label_track.append(content[:-1])
        all_labels[content[:-1]] = None
        continue
    else:
        pass3.append({
            'line': line['line'],
            'content': {'tokens': content.split(), 'labels': label_track},
            'og': line['content']
        })
        label_track = []

print_pass(pass3)

pass4 = []
for line in pass3:
    tokens = line['content']['tokens']
    labels = line['content']['labels']
    for label in labels:
        all_labels[label] = sum([len(x['content']) for x in pass4])
    if replacements[tokens[0].lower()] == 'HALT':
        if len(tokens) != 1:
            error(f'invalid HALT instruction "{line["og"]}" on line {line["line"]}. Expected 1 tokens, got {len(tokens)}.')
        pass4.append({'line': line['line'], 'content': [0]})

    elif replacements[tokens[0].lower()] == 'NOP':
        if len(tokens) != 1:
            error(f'invalid NOP instruction "{line["og"]}" on line {line["line"]}. Expected 1 tokens, got {len(tokens)}.')
        pass4.append({'line': line['line'], 'content': [1]})

    elif replacements[tokens[0].lower()] == 'SET':
        if len(tokens) != 3:
            error(f'invalid SET instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)
        value = parse_value(tokens[2], line)

        pass4.append({'line': line['line'], 'content': [2, addr, value]})

    elif replacements[tokens[0].lower()] == 'OPR':
        if len(tokens) != 5:
            error(f'invalid OPR instruction "{line["og"]}" on line {line["line"]}. Expected 5 tokens, got {len(tokens)}.')

        opetaion_options = [
            'add',
            'sub',
            'mul',
            'div',
            'mod',
            'pow',
        ]
        operation = tokens[1].lower()
        if operation not in replacements:
            error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
        operation = replacements[operation]

        if operation not in opetaion_options:
            error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
        operation = opetaion_options.index(operation.lower())
        addr1 = parse_value(tokens[2], line)
        addr2 = parse_value(tokens[3], line)
        addr3 = parse_value(tokens[4], line)

        pass4.append({'line': line['line'], 'content': [3, operation, addr1, addr2, addr3]})

    elif replacements[tokens[0].lower()] == 'ONC':
        if len(tokens) != 5:
            error(f'invalid ONC instruction "{line["og"]}" on line {line["line"]}. Expected 5 tokens, got {len(tokens)}.')
        opetaion_options = [
            'add',
            'sub',
            'mul',
            'div',
            'mod',
            'pow',
            'rsub',
            'rdiv',
            'rmod',
            'rpow',
        ]
        operation = tokens[1].lower()
        if operation not in replacements:
            error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
        operation = replacements[operation]

        if operation not in opetaion_options:
            error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
        operation = opetaion_options.index(operation.lower())
        addr1 = parse_value(tokens[2], line)
        addr2 = parse_value(tokens[3], line)
        addr3 = parse_value(tokens[4], line)

        pass4.append({'line': line['line'], 'content': [4, operation, addr1, addr2, addr3]})

    elif replacements[tokens[0].lower()] == 'RJMP':
        if len(tokens) != 2:
            error(f'invalid RJMP instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        delta = parse_value(tokens[1], line)
        if type(delta) == str:
            if delta.startswith('!'):
                warn(f'RJMP instruction uses relative addressing, but "{delta}" is an absolute address on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [5, 1, delta]})

    elif replacements[tokens[0].lower()] == 'JMP':
        if len(tokens) != 2:
            error(f'invalid JMP instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)
        if type(addr) == str:
            if addr.startswith('~'):
                warn(f'JMP instruction uses absolute addressing, but "{addr}" is a relative address on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [5, 0, addr]})

    elif replacements[tokens[0].lower()] == 'RJMA':
        if len(tokens) != 2:
            error(f'invalid RJMA instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)
        if type(addr) == str:
            if addr.startswith('!'):
                warn(f'RJMA instruction reads jump delta from RAM, but an absolute address "{addr}" was given on line {line["line"]}.')
            if addr.startswith('~'):
                warn(f'RJMA instruction reads jump delta from RAM, but a relative address "{addr}" was given on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [6, 1, addr]})

    elif replacements[tokens[0].lower()] == 'JMA':
        if len(tokens) != 2:
            error(f'invalid JMA instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)
        if type(addr) == str:
            if not addr.startswith('!'):
                warn(f'JMA instruction reads jump address from RAM, but an absolute address "{addr}" was given on line {line["line"]}.')
            if not addr.startswith('~'):
                warn(f'JMA instruction reads jump address from RAM, but a relative address "{addr}" was given on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [6, 0, addr]})

    elif replacements[tokens[0].lower()] == 'JMIF':
        if len(tokens) != 5:
            error(f'invalid JMIF instruction "{line["og"]}" on line {line["line"]}. Expected 5 tokens, got {len(tokens)}.')
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
        if operation not in replacements:
            error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
        operation = replacements[operation]
        num1 = tokens[2]
        num2 = tokens[3]
        if operation in flipOperation:
            num2 = tokens[2]
            num1 = tokens[3]
            operation = flipOperation[operation]
        if operation not in opetaion_options:
            error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
        operation = opetaion_options.index(operation.lower())
        addr1 = parse_value(num1, line)
        addr2 = parse_value(num2, line)
        delta = parse_value(tokens[4], line)
        if type(addr) == str:
            if addr.startswith('!'):
                warn(f'JMIF instruction uses relative addressing, but "{delta}" is an absolute address on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [7, operation, addr1, addr2, delta]})

    elif replacements[tokens[0].lower()] == 'M':
        if len(tokens) != 3:
            error(f'invalid M instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

        addr1 = parse_value(tokens[1], line)
        addr2 = parse_value(tokens[2], line)

        pass4.append({'line': line['line'], 'content': [8, addr1, addr2]})

    elif replacements[tokens[0].lower()] == 'RM':
        if len(tokens) != 3:
            error(f'invalid RMV instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

        addr1 = parse_value(tokens[1], line)
        addr2 = parse_value(tokens[2], line)

        pass4.append({'line': line['line'], 'content': [9, addr1, addr2]})

    elif replacements[tokens[0].lower()] == 'MR':
        if len(tokens) != 3:
            error(f'invalid RMV instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

        addr1 = parse_value(tokens[1], line)
        addr2 = parse_value(tokens[2], line)

        pass4.append({'line': line['line'], 'content': [10, addr1, addr2]})

    elif replacements[tokens[0].lower()] == 'RMR':
        if len(tokens) != 3:
            error(f'invalid RMR instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

        addr1 = parse_value(tokens[1], line)
        addr2 = parse_value(tokens[2], line)

        pass4.append({'line': line['line'], 'content': [11, addr1, addr2]})

    elif replacements[tokens[0].lower()] == 'PRI':
        if len(tokens) != 2:
            error(f'invalid PRI instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        value = parse_value(tokens[1], line)

        pass4.append({'line': line['line'], 'content': [12, value]})

    elif replacements[tokens[0].lower()] == 'PRIA':
        if len(tokens) != 2:
            error(f'invalid PRIA instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)

        pass4.append({'line': line['line'], 'content': [13, addr]})

    else:
        error(f'invalid instruction "{line["og"]}" on line {line["line"]}')

print_pass(pass4)

cmd_start_index = 0
pass5 = []

def smart_parse(value, line):
    if type(value) in [int, float]:
        return value
    if value.startswith('!'):
        label = all_labels[value[1:]]
        return label
    if value.startswith('~'):
        label = all_labels[value[1:]]
        return label - cmd_start_index
    if value.startswith('@'):
        return smart_parse(definitions[value[1:]], line)
    try:
        return int(value) if value.isdigit() else float(value)
    except ValueError:
        error(f'invalid value "{value}" on line {line["line"]}')
for line in pass4:
    # pass5.append('\n')
    cmd_start_index = len(pass5)
    for cmd in line['content']:
        if type(cmd) != str:
            pass5.append(cmd)
            continue
        pass5.append(smart_parse(cmd, line))

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
print()
print('\n'.join([' '.join(line) for line in print_thing]))

with open("C:\Program Files (x86)\Steam\steamapps\common\Scrap Mechanic\Data\Importer\Importer.json", "w") as out_file:
    json.dump(pass5, out_file, indent = 4)

dump_filename = '.'.join(filename.split('.')[:-1]+['num', 'json'])
with open(dump_filename, 'w') as out_file:
    json.dump(pass5, out_file, indent = 4)

if '--run' in sys.argv:
    import subprocess
    subprocess.run([sys.executable, 'emulator.py', dump_filename], shell=True)
