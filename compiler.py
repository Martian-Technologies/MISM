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
                    parts.append(collected_statement.strip()) if collected_statement.strip() else None
                    collected_statement = ''
                continue
        return parts