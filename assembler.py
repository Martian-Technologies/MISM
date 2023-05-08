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
    'MOV',
    'RTA',
    'RTR',
    'PRNT',
    'PRTA',
]

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
    if tokens[0] == 'HALT':
        if len(tokens) != 1:
            error(f'invalid HALT instruction "{line["og"]}" on line {line["line"]}. Expected 1 tokens, got {len(tokens)}.')
        pass4.append({'line': line['line'], 'content': [0]})

    elif tokens[0] == 'NOP':
        if len(tokens) != 1:
            error(f'invalid NOP instruction "{line["og"]}" on line {line["line"]}. Expected 1 tokens, got {len(tokens)}.')
        pass4.append({'line': line['line'], 'content': [1]})

    elif tokens[0] == 'SET':
        if len(tokens) != 3:
            error(f'invalid SET instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)
        value = parse_value(tokens[2], line)

        pass4.append({'line': line['line'], 'content': [2, addr, value]})

    elif tokens[0] == 'OPR':
        if len(tokens) != 5:
            error(f'invalid OPR instruction "{line["og"]}" on line {line["line"]}. Expected 5 tokens, got {len(tokens)}.')

        operation = tokens[1]
        opetaion_options = [
            'ADD',
            'SUB',
            'MUL',
            'DIV',
            'MOD',
        ]
        if operation not in opetaion_options:
            error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
        operation = opetaion_options.index(operation)
        addr1 = parse_value(tokens[2], line)
        addr2 = parse_value(tokens[3], line)
        addr3 = parse_value(tokens[4], line)

        pass4.append({'line': line['line'], 'content': [3, operation, addr1, addr2, addr3]})

    elif tokens[0] == 'ONC':
        if len(tokens) != 5:
            error(f'invalid ONC instruction "{line["og"]}" on line {line["line"]}. Expected 5 tokens, got {len(tokens)}.')

        operation = tokens[1]
        opetaion_options = [
            'ADD',
            'SUB',
            'MUL',
            'DIV',
            'MOD',
            'RSUB',
            'RDIV',
            'RMOD',
        ]
        if operation not in opetaion_options:
            error(f'invalid operation "{operation}" on line {line["line"]}. Expected one of {opetaion_options}, got "{operation}".')
        operation = opetaion_options.index(operation)
        addr1 = parse_value(tokens[2], line)
        addr2 = parse_value(tokens[3], line)
        addr3 = parse_value(tokens[4], line)

        pass4.append({'line': line['line'], 'content': [4, operation, addr1, addr2, addr3]})

    elif tokens[0] == 'RJMP':
        if len(tokens) != 2:
            error(f'invalid RJMP instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        delta = parse_value(tokens[1], line)
        if type(delta) == str:
            if delta.startswith('!'):
                warn(f'RJMP instruction uses relative addressing, but "{delta}" is an absolute address on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [5, 1, delta]})

    elif tokens[0] == 'JMP':
        if len(tokens) != 2:
            error(f'invalid JMP instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)
        if type(addr) == str:
            if addr.startswith('~'):
                warn(f'JMP instruction uses absolute addressing, but "{addr}" is a relative address on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [5, 0, addr]})

    elif tokens[0] == 'RJMA':
        if len(tokens) != 2:
            error(f'invalid RJMA instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)
        if type(addr) == str:
            if addr.startswith('!'):
                warn(f'RJMA instruction reads jump delta from RAM, but an absolute address "{addr}" was given on line {line["line"]}.')
            if addr.startswith('~'):
                warn(f'RJMA instruction reads jump delta from RAM, but a relative address "{addr}" was given on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [6, 1, addr]})

    elif tokens[0] == 'JMA':
        if len(tokens) != 2:
            error(f'invalid JMA instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)
        if type(addr) == str:
            if not addr.startswith('!'):
                warn(f'JMA instruction reads jump address from RAM, but an absolute address "{addr}" was given on line {line["line"]}.')
            if not addr.startswith('~'):
                warn(f'JMA instruction reads jump address from RAM, but a relative address "{addr}" was given on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [6, 0, addr]})

    elif tokens[0] == 'JMIF':
        if len(tokens) != 2:
            error(f'invalid JMIF instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)
        if type(addr) == str:
            if addr.startswith('!'):
                warn(f'JMIF instruction uses relative addressing, but "{delta}" is an absolute address on line {line["line"]}.')

        pass4.append({'line': line['line'], 'content': [7, addr]})

    elif tokens[0] == 'MOV':
        if len(tokens) != 3:
            error(f'invalid MOV instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

        addr1 = parse_value(tokens[1], line)
        addr2 = parse_value(tokens[2], line)

        pass4.append({'line': line['line'], 'content': [8, addr1, addr2]})

    elif tokens[0] == 'RMV':
        if len(tokens) != 3:
            error(f'invalid RMV instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

        addr1 = parse_value(tokens[1], line)
        addr2 = parse_value(tokens[2], line)

        pass4.append({'line': line['line'], 'content': [9, addr1, addr2]})

    elif tokens[0] == 'RMR':
        if len(tokens) != 3:
            error(f'invalid RMR instruction "{line["og"]}" on line {line["line"]}. Expected 3 tokens, got {len(tokens)}.')

        addr1 = parse_value(tokens[1], line)
        addr2 = parse_value(tokens[2], line)

        pass4.append({'line': line['line'], 'content': [10, addr1, addr2]})

    elif tokens[0] == 'PRNT':
        if len(tokens) != 2:
            error(f'invalid PRNT instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        value = parse_value(tokens[1], line)

        pass4.append({'line': line['line'], 'content': [11, value]})

    elif tokens[0] == 'PRTA':
        if len(tokens) != 2:
            error(f'invalid PRTA instruction "{line["og"]}" on line {line["line"]}. Expected 2 tokens, got {len(tokens)}.')

        addr = parse_value(tokens[1], line)

        pass4.append({'line': line['line'], 'content': [12, addr]})

    else:
        error(f'invalid instruction "{line["og"]}" on line {line["line"]}')

print_pass(pass4)

cmd_start_len = 0
pass5 = []

def smart_parse(value, line):
    if type(value) in [int, float]:
        return value
    if value.startswith('!'):
        label = all_labels[value[1:]]
        return label
    if value.startswith('~'):
        label = all_labels[value[1:]]
        return label - cmd_start_len
    if value.startswith('@'):
        return smart_parse(definitions[value[1:]], line)
    try:
        return int(value) if value.isdigit() else float(value)
    except ValueError:
        error(f'invalid value "{value}" on line {line["line"]}')
for line in pass4:
    # pass5.append('\n')
    cmd_start_len = len(pass5)
    for cmd in line['content']:
        if type(cmd) != str:
            pass5.append(cmd)
            continue
        pass5.append(smart_parse(cmd, line))

print(all_labels)

print(' '.join([str(x) for x in pass5]))

out_file = open("C:\Program Files (x86)\Steam\steamapps\common\Scrap Mechanic\Data\Importer\Importer.json", "w")
  
json.dump(pass5, out_file, indent = 4)

if '--run' in sys.argv:
    import subprocess
    subprocess.run(['python3', 'emulator.py', '.'.join(filename.split('.')[:-1] + ['num', 'json'])])
