class Compiler:
    """used to compile code into assembly code"""

    @staticmethod
    def parse(code):
        cmds = []
        collected_statement = ''
        backslash = False
        bracket_stack = []
        line = 0
        for char in code.strip():
            if char == '\n':
                line += 1
            if backslash:
                collected_statement += char
                backslash = False
                continue
            if char == '\\':
                backslash = True
                continue
            if char == '"':
                if bracket_stack and bracket_stack[-1] == '"':
                    bracket_stack.pop()
                else:
                    bracket_stack.append('"')
            if char == '[':
                bracket_stack.append('[')
            if char == ']':
                if bracket_stack and bracket_stack[-1] == '[':
                    bracket_stack.pop()
                else:
                    raise Exception(f'Unmatched bracket ] on line {line}')
            if char == '(':
                bracket_stack.append('(')
            if char == ')':
                if bracket_stack and bracket_stack[-1] == '(':
                    bracket_stack.pop()
                else:
                    raise Exception(f'Unmatched bracket ) on line {line}')
            if char == '{':
                bracket_stack.append('{')
            if char == '}':
                if bracket_stack and bracket_stack[-1] == '{':
                    bracket_stack.pop()
                else:
                    raise Exception(f'Unmatched bracket {"}"} on line {line}')
            if char == ';' and not bracket_stack:
                if collected_statement:
                    cmds.append(collected_statement.strip())
                    collected_statement = ''
                continue
            if char == '}' and not bracket_stack:
                if collected_statement:
                    cmds.append((collected_statement+'}').strip())
                    collected_statement = ''
                continue
            collected_statement += char
            print(collected_statement)
        return cmds