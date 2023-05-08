import sys
import os

filename = 'test.mas'
if len(sys.argv) > 1:
    filename = sys.argv[1]

if not os.path.exists(filename):
    print(f'Error: file "{filename}" not found')
    exit(1)

opcodes = [
    'NOP',
    'SET',
    'OPR',
    'ONC',
    'JMP',
    'JMI',
    'HALT',
    'PRNT',
    'PRTA',
    'GMP',
    'GMA',
    'MOV'
]

def parse_value(value, line):
    if value.startswith('@'):
        if value not in constants:
            print(f'Error: undefined constant "{value}" on line {line}')
            exit(1)
        return constants[value]
    if value.startswith('!') or value.startswith('~!'):
        return value
    try:
        value = int(value) if '.' not in value else float(value)
    except ValueError:
        print(f'Error: invalid value "{value}" on line {line}')
        exit(1)
    return value

pass1 = []
constants = {}
flags = {}
with open(filename, 'r') as f:
    for line in f:
        line = line.strip().split('#')[0].strip()
        if line == '':
            continue
        if line[0] == ';':
            continue
        if line.startswith('@define'):
            _, name, value = line.split()
            constants['@'+name] = float(value) if '.' in value else int(value)
            continue
        pass1.append(line)

pass2 = []
for line in pass1:
    for const in sorted(list(constants.keys()), key=lambda x: len(x), reverse=True):
        line = line.replace(const, str(constants[const]))
    pass2.append(line)

pass3 = []
for i, line in enumerate(pass2):
    things = line.split(':')
    lin = things[0].strip()
    for flag in things[1:]:
        flags[flag.strip()] = i+1
    pass3.append({'line': i+1, 'tokens': lin.split()})
pass4 = []
for line in pass3:
    if line['tokens'][0] not in opcodes:
        print(f'Error: invalid opcode "{line["tokens"][0]}" on line {line["line"]}')
        exit(1)

    if line['tokens'][0] == 'NOP':
        if len(line['tokens']) != 1:
            print(f'Error: invalid number of arguments for opcode "NOP" on line {line["line"]}')
            exit(1)
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': []})

    elif line['tokens'][0] == 'SET':
        if len(line['tokens']) != 3:
            print(f'Error: invalid number of arguments for opcode "SET" on line {line["line"]}')
            exit(1)
        addr = parse_value(line['tokens'][1], line['line'])
        value = parse_value(line['tokens'][2], line['line'])
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [addr, value]})

    elif line['tokens'][0] == 'OPR':
        if len(line['tokens']) != 5:
            print(f'Error: invalid number of arguments for opcode "OPR" on line {line["line"]}')
            exit(1)
        operation = line['tokens'][1]
        if operation not in ['ADD', 'SUB', 'MUL', 'DIV', 'MOD']:
            print(f'Error: invalid operation "{operation}" on line {line["line"]}')
            exit(1)
        addr1 = parse_value(line['tokens'][2], line['line'])
        addr2 = parse_value(line['tokens'][3], line['line'])
        addr3 = parse_value(line['tokens'][4], line['line'])
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [['ADD', 'SUB', 'MUL', 'DIV', 'MOD'].index(operation), addr1, addr2, addr3]})

    elif line['tokens'][0] == 'ONC':
        if len(line['tokens']) != 5:
            print(f'Error: invalid number of arguments for opcode "ONC" on line {line["line"]}')
            exit(1)
        operation = line['tokens'][1]
        if operation not in ['ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'RSUB', 'RDIV', 'RMOD']:
            print(f'Error: invalid operation "{operation}" on line {line["line"]}')
            exit(1)
        addr1 = parse_value(line['tokens'][2], line['line'])
        value = parse_value(line['tokens'][3], line['line'])
        addr2 = parse_value(line['tokens'][4], line['line'])
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [['ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'RSUB', 'RDIV', 'RMOD'].index(operation), addr1, value, addr2]})
        
    elif line['tokens'][0] == 'JMP':
        if len(line['tokens']) != 2:
            print(f'Error: invalid number of arguments for opcode "JMP" on line {line["line"]}')
            exit(1)
        delta = parse_value(line['tokens'][1], line['line'])
        if str(delta).startswith('!'):
            delta = '~'+delta
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [delta]})

    elif line['tokens'][0] == 'JMI':
        if len(line['tokens']) != 5:
            print(f'Error: invalid number of arguments for opcode "JMI" on line {line["line"]}')
            exit(1)
        op = line['tokens'][1]
        if op not in ['EQU', 'NEQ', 'LSS', 'LEQ']:
            print(f'Error: invalid operation "{op}" on line {line["line"]}')
            exit(1)
        addr1 = parse_value(line['tokens'][2], line['line'])
        addr2 = parse_value(line['tokens'][3], line['line'])
        delta = parse_value(line['tokens'][4], line['line'])
        if str(delta).startswith('!'):
            delta = '~'+delta
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [['EQU', 'NEQ', 'LSS', 'LEQ'].index(op), addr1, addr2, delta]})

    elif line['tokens'][0] == 'HALT':
        if len(line['tokens']) != 1:
            print(f'Error: invalid number of arguments for opcode "HALT" on line {line["line"]}')
            exit(1)
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': []})

    elif line['tokens'][0] == 'PRNT':
        if len(line['tokens']) != 2:
            print(f'Error: invalid number of arguments for opcode "PRNT" on line {line["line"]}')
            exit(1)
        value = parse_value(line['tokens'][1], line['line'])
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [value]})

    elif line['tokens'][0] == 'PRTA':
        if len(line['tokens']) != 2:
            print(f'Error: invalid number of arguments for opcode "PRTA" on line {line["line"]}')
            exit(1)
        addr = parse_value(line['tokens'][1], line['line'])
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [addr]})

    elif line['tokens'][0] == 'GMP':
        if len(line['tokens']) != 2:
            print(f'Error: invalid number of arguments for opcode "GMP" on line {line["line"]}')
            exit(1)
        addr = parse_value(line['tokens'][1], line['line'])
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [addr]})

    elif line['tokens'][0] == 'GMA':
        if len(line['tokens']) != 2:
            print(f'Error: invalid number of arguments for opcode "GMA" on line {line["line"]}')
            exit(1)
        addr = parse_value(line['tokens'][1], line['line'])
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [addr]})

    elif line['tokens'][0] == 'MOV':
        if len(line['tokens']) != 3:
            print(f'Error: invalid number of arguments for opcode "MOV" on line {line["line"]}')
            exit(1)
        addr1 = parse_value(line['tokens'][1], line['line'])
        addr2 = parse_value(line['tokens'][2], line['line'])
        pass4.append({'line': line['line'], 'opcode': line['tokens'][0], 'arg': [addr1, addr2]})

    else:
        print(f'Error: invalid opcode "{line["tokens"][0]}" on line {line["line"]}')
        exit(1)


line_to_addr = {}
pass5 = []
for line in pass4:
    line_to_addr[line['line']] = len(pass5)
    pass5.append(opcodes.index(line['opcode']))
    pass5.extend(line['arg'])

pass6 = []
for i, line in enumerate(pass5):
    if type(line) in [float, int]:
        pass6.append(line)
    else:
        if line.startswith('~!'):
            flag = line[2:]
            if flag not in flags:
                print(f'Error: invalid flag "{flag}"')
                exit(1)
            pass6.append(line_to_addr[flags[flag]]-i-1)
        elif line.startswith('!'):
            flag = line[1:]
            if flag not in flags:
                print(f'Error: invalid flag "{flag}"')
                exit(1)
            pass6.append(line_to_addr[flags[flag]])
        else:
            print(f'Error: invalid address "{line}"')
            exit(1)

print(' '.join([str(x) for x in pass6]))

import json
with open('pass1.json', 'w') as f:
    json.dump(pass1, f, indent=4)
with open('pass2.json', 'w') as f:
    json.dump(pass2, f, indent=4)
with open('pass3.json', 'w') as f:
    json.dump(pass3, f, indent=4)
with open('pass4.json', 'w') as f:
    json.dump(pass4, f, indent=4)
with open('pass5.json', 'w') as f:
    json.dump(pass5, f, indent=4)

with open('.'.join(filename.split('.')[:-1]+['num', 'json']), 'w') as f:
    json.dump(pass6, f, indent=4)

if sys.argv[-1] == '--run':
    import subprocess
    subprocess.run(['python3', 'emulator.py', '.'.join(filename.split('.')[:-1]+['num', 'json'])])