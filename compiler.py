from codeSpliter import CodeSpliter

class Compiler:
    """used to compile code into assembly code"""

    reserved = {
        'if': 'IF',
        'then': 'THEN',
        'else': 'ELSE',
        'while': 'WHILE',
        'do': 'DO',
        'end': 'END',
        'print': 'PRINT',
        'for': 'FOR'
    }

    """
    Please use functions to make code easier to read.
    You have a horibal habit to make all the code in one giant block.
    Please make helper functions. You should have a ton, you have one.
    """

    @staticmethod
    def compile(inputCode):
        """
        Compiles code into assembly.\n
        Input a string containing all the code that you want to compile.
        """
        code = CodeSpliter.split(inputCode)
        print(code)
        return code
        # parsedCode = Compiler.partition(inputCode)
        # piecedCode = Compiler.piece(parsedCode)
        # return piecedCode


    @staticmethod
    def partition(code):
        parts = []
        collected_statement = ''
        backslash = False
        bracket_stack = []
        for char in code:
            if char == '\n':
                continue
            if char == '\\':
                backslash = True
                continue
            if backslash:
                collected_statement += '\\'
                backslash = False
                continue
            semicol = False
            if char in '([{':
                if not bracket_stack:
                    parts.append(collected_statement.strip()) if collected_statement.strip() else None
                    collected_statement = ''
                bracket_stack.append(char)
            if char in ')]}':
                if not bracket_stack:
                    raise Exception('bracket mismatch')
                if char == ')' and bracket_stack[-1] != '(':
                    raise Exception('bracket mismatch')
                if char == ']' and bracket_stack[-1] != '[':
                    raise Exception('bracket mismatch')
                if char == '}' and bracket_stack[-1] != '{':
                    raise Exception('bracket mismatch')
                bracket_stack.pop()
                if not bracket_stack:
                    semicol = True
            collected_statement += char
            if char == ';' and not bracket_stack:
                semicol = True
            if semicol:
                if collected_statement:
                    parts.append(collected_statement.strip()) if collected_statement.strip() and collected_statement.strip()!=';' else None
                    collected_statement = ''
                continue
        return parts
    
    """
    Look how much better this is.
    Please use functions.
    """

    @staticmethod
    def piece(parsed):
        print(parsed)
        logic_tree = []
        current_command = None
        parsed_code = parsed.copy()
        while len(parsed_code) > 0:
            if current_command is None:
                current_command = Compiler.getCommandType(parsed_code.pop(0))
            else:
                current_command = Compiler.getCommandData(current_command, parsed_code, logic_tree)
        if current_command is not None:
            logic_tree.append(current_command)
        return logic_tree


    @staticmethod
    def getCommandType(part):
        if part == 'for':
            current_command = {
                'type': 'for',
                'init': None,
                'condition': None,
                'increment': None,
                'code': None
            }
        elif part == 'if':
            current_command = {
                'type': 'if',
                'condition_code_pairs': [],
                'next_statement': 'if'
            }
        elif part == 'while':
            current_command = {
                'type': 'while',
                'condition': None,
                'code': None
            }
        elif part == 'do':
            current_command = {
                'type': 'dowhile',
                'code': None,
                'condition': None
            }
        elif part == 'print':
            current_command = {
                'type': 'print',
                'expression': None
            }
        elif part.split(' ')[0] == 'func':
            current_command = {
                'type': 'function',
                'name': part.split(' ')[1],
                'args': None,
                'code': None
            }
        else:
            current_command = {
                'type': 'expression',
                'expression': [part]
            }
        return current_command

    @staticmethod
    def getCommandData(current_command, parsed_code, logic_tree):
        # for loops
        if current_command['type'] == 'for':
            part = parsed_code.pop(0)
            if not part.startswith('('):
                raise Exception('expected "("')
            part = part[1:]
            if not part.endswith(')'):
                raise Exception('expected ")"')
            part = part[:-1]
            part = part.split(';')
            if len(part) != 3:
                raise Exception('expected 3 parts in for loop')
            current_command['init'] = part[0]
            current_command['condition'] = part[1]
            current_command['increment'] = part[2]
            code_chunk = parsed_code.pop(0)
            if not code_chunk.startswith('{'):
                raise Exception('expected "{"')
            code_chunk = code_chunk[1:]
            if not code_chunk.endswith('}'):
                raise Exception('expected "}"')
            code_chunk = code_chunk[:-1]
            current_command['code'] = Compiler.piece(Compiler.partition(code_chunk))
            logic_tree.append(current_command)
            current_command = None

        # if statements
        elif current_command['type'] == 'if':
            part = parsed_code.pop(0)
            next_statement = current_command['next_statement']
            if next_statement == 'if':
                if not part.startswith('('):
                    raise Exception('expected "("')
                part = part[1:]
                if not part.endswith(')'):
                    raise Exception('expected ")"')
                part = part[:-1]
                current_command['condition_code_pairs'].append({
                    'condition': part,
                    'code': None
                })
                code_chunk = parsed_code.pop(0)
                if not code_chunk.startswith('{'):
                    raise Exception('expected "{"')
                code_chunk = code_chunk[1:]
                if not code_chunk.endswith('}'):
                    raise Exception('expected "}"')
                code_chunk = code_chunk[:-1]
                current_command['condition_code_pairs'][-1]['code'] = Compiler.piece(Compiler.partition(code_chunk))
                part = parsed_code.pop(0)
                if part == 'else':
                    current_command['next_statement'] = 'else'
                elif part == 'elif':
                    current_command['next_statement'] = 'if'
                else:
                    current_command['next_statement'] = None
                    parsed_code.insert(0, part)
            
            # else statements after if statements
            elif next_statement == 'else':
                if not part.startswith('{'):
                    raise Exception('expected "{"')
                part = part[1:]
                if not part.endswith('}'):
                    raise Exception('expected "}"')
                part = part[:-1]
                current_command['condition_code_pairs'].append({
                    'condition': None,
                    'code': part
                })
                current_command['next_statement'] = None
                current_command = None
            else:
                raise Exception('unknown next statement')

        # while loops
        elif current_command['type'] == 'while':
            part = parsed_code.pop(0)
            if not part.startswith('('):
                raise Exception('expected "("')
            part = part[1:]
            if not part.endswith(')'):
                raise Exception('expected ")"')
            part = part[:-1]
            current_command['condition'] = part
            code_chunk = parsed_code.pop(0)
            if not code_chunk.startswith('{'):
                raise Exception('expected "{"')
            code_chunk = code_chunk[1:]
            if not code_chunk.endswith('}'):
                raise Exception('expected "}"')
            code_chunk = code_chunk[:-1]
            current_command['code'] = Compiler.piece(Compiler.partition(code_chunk))
            logic_tree.append(current_command)
            current_command = None
        
        # do while loops
        elif current_command['type'] == 'dowhile':
            code_chunk = parsed_code.pop(0)
            if not code_chunk.startswith('{'):
                raise Exception('expected "{"')
            code_chunk = code_chunk[1:]
            if not code_chunk.endswith('}'):
                raise Exception('expected "}"')
            code_chunk = code_chunk[:-1]
            current_command['code'] = Compiler.piece(Compiler.partition(code_chunk))
            part = parsed_code.pop(0)
            if not part.startswith('('):
                raise Exception('expected "("')
            part = part[1:]
            if not part.endswith(')'):
                raise Exception('expected ")"')
            part = part[:-1]
            current_command['condition'] = part
            logic_tree.append(current_command)
            current_command = None

        # prints
        elif current_command['type'] == 'print':
            part = parsed_code.pop(0)
            if not part.startswith('('):
                raise Exception('expected "("')
            part = part[1:]
            if not part.endswith(')'):
                raise Exception('expected ")"')
            part = part[:-1]
            current_command['expression'] = part
            logic_tree.append(current_command)
            current_command = None

        # functions
        elif current_command['type'] == 'function':
            part = parsed_code.pop(0)
            if not part.startswith('('):
                raise Exception('expected "("')
            part = part[1:]
            if not part.endswith(')'):
                raise Exception('expected ")"')
            part = part[:-1]
            current_command['args'] = [x.strip() for x in part.split(',')]
            code_chunk = parsed_code.pop(0)
            if not code_chunk.startswith('{'):
                raise Exception('expected "{"')
            code_chunk = code_chunk[1:]
            if not code_chunk.endswith('}'):
                raise Exception('expected "}"')
            code_chunk = code_chunk[:-1]
            current_command['code'] = Compiler.piece(Compiler.partition(code_chunk))
            logic_tree.append(current_command)
            current_command = None
        else:
            raise Exception('unknown command type')
        return current_command