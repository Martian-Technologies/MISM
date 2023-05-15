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
        line = 0
        for char in code:
            print(bracket_stack)
            if char == '\n':
                line += 1
            if backslash:
                backslash = False
                collected_statement += char
                continue
            if char == '\\':
                backslash = True
                continue
            if char == '(':
                if not bracket_stack:
                    parts.append(collected_statement)
                    collected_statement = ''
                bracket_stack.append('(')
            elif char == ')':
                if not bracket_stack:
                    raise Exception(f'Unexpected ")" at line {line}')
                if bracket_stack[-1] in ['"', "'"]:
                    collected_statement += char
                    continue
                if bracket_stack[-1] != '(':
                    raise Exception(f'Unexpected ")" at line {line}')
                bracket_stack.pop()
            elif char == '[':
                if not bracket_stack:
                    parts.append(collected_statement)
                    collected_statement = ''
                bracket_stack.append('[')
            elif char == ']':
                if not bracket_stack:
                    raise Exception(f'Unexpected "]" at line {line}')
                if bracket_stack[-1] in ['"', "'"]:
                    collected_statement += char
                    continue
                if bracket_stack[-1] != '[':
                    raise Exception(f'Unexpected "]" at line {line}')
                bracket_stack.pop()
            elif char == '{':
                if not bracket_stack:
                    parts.append(collected_statement)
                    collected_statement = ''
                bracket_stack.append('{')
            elif char == '}':
                if not bracket_stack:
                    raise Exception(f'Unexpected "{"}"}" at line {line}')
                if bracket_stack[-1] in ['"', "'"]:
                    collected_statement += char
                    continue
                if bracket_stack[-1] != '{':
                    raise Exception(f'Unexpected "{"}"}" at line {line}')
                bracket_stack.pop()
            collected_statement += char
            if char in ';)}]':
                if not bracket_stack:
                    parts.append(collected_statement)
                    collected_statement = ''
        parts = [part.strip() for part in parts if part.strip()]
        return parts