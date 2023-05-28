if __name__ == "__main__":
    import main

class CodeSpliter:
    @staticmethod
    def split(code, splitTypes = {';'}):
        lines = CodeSpliter.split_on_types_and_stuff(code, splitTypes)
        chunks = CodeSpliter.split_chunks(lines)
        return chunks
        
    @staticmethod
    def split_on_types_and_stuff(code, split_types):        
        lines = []
        line = ''
        i = 0
        isSetting = False
        while i < len(code):
            char = code[i]
            if char in split_types:
                if not (CodeSpliter.if_only_has(line, {' '}) or len(line) == 0):
                    lines.append(line)
                line = ''
            elif char == '{':
                i, line = CodeSpliter.get_brace_block(i, line, code)
                lines.append(line)
                line = ''
            elif char == '(':
                i, line = CodeSpliter.get_brace_block(i, line, code, '(', ')')
            elif char == '/' and i+1 < len(code):
                if code[i+1] == '/':
                    i = CodeSpliter.get_next_char_pos(code, i)
            elif char == '@':
                isSetting = True
                line += char
            elif char != '\n' and (len(line) > 0 or char != ' '):
                line += char
            elif char == '\n':
                if isSetting:
                    isSetting = False
                    lines.append(line)
                    line = ''
            
            i += 1
        if len(line) != 0:
            split_types_list = list(split_types)
            if len(split_types_list) == 1:
                split_types_readable = split_types_list[0]
            elif len(split_types_list) == 2:
                split_types_readable = f'{split_types_list[0]} or {split_types_list[1]}'
            else:
                split_types_readable = f"{', '.join(split_types_list[:-1])}, or {split_types_list[-1]}"
            raise Exception(f"statement '{line}' on char {i} needs to end with {split_types_readable}")
        return lines
    
    @staticmethod
    def split_chunks(lines):
        allChucks = []
        for line in lines:
            chunks = []
            chunk = ''
            i = 0
            while i < len(line):
                char = line[i]
                if char == '{':
                    if not (CodeSpliter.if_only_has(chunk, {' '}) or len(chunk) == 0):
                        chunks.append(chunk)
                    i, block = CodeSpliter.get_brace_block(i, '', line, includeBrace=False)
                    chunk = CodeSpliter.split(block)
                    chunks.append(chunk)
                    chunk = ''
                elif char == '(':
                    if not (CodeSpliter.if_only_has(chunk, {' '}) or len(chunk) == 0):
                        chunks.append(chunk)
                    i, block = CodeSpliter.get_brace_block(i, '', line, '(', ')', False)
                    block += ';'
                    chunk = CodeSpliter.split(block, {';', ','})
                    chunks.append(chunk)
                    chunk = ''
                elif char == ' ':
                    if not (CodeSpliter.if_only_has(chunk, {' '}) or len(chunk) == 0):
                        chunk = CodeSpliter.split_on_operators(chunk, chunks)
                        if len(chunk) != 0:
                            chunks.append(chunk)
                    chunk = ''
                else:
                    chunk += char
                i += 1
            if not (CodeSpliter.if_only_has(chunk, {' '}) or len(chunk) == 0):
                chunk = CodeSpliter.split_on_operators(chunk, chunks)
                if len(chunk) != 0:
                    chunks.append(chunk)
            allChucks.append(chunks)
        return allChucks
    
    @staticmethod
    def if_only_has(string, chars):
        for char in string:
            if not char in chars:
                return False
        return True
    
    @staticmethod
    def get_brace_block(start, line, code, braceOpen = '{', braceClose = '}', includeBrace = True):
        if includeBrace:
            line += braceOpen
        braceCounter = 1
        while braceCounter > 0:
            start += 1
            if start >= len(code):
                raise Exception(f'did not close curly brace type {braceOpen}{braceClose} on line {code}')
            char = code[start]
            if char == braceOpen:
                braceCounter += 1
            elif char == braceClose:
                braceCounter -= 1
            if includeBrace or braceCounter > 0:
                line += char
        return start, line
    
    @staticmethod
    def string_contain_strings(string, strings):
        for s in strings:
            i = string.find(s)
            if i != -1:
                return i, s
        return -1, ''
    
    @staticmethod
    def split_on_operators(chunk, chunks):
        operators = ['=', ':=', '+', '-', '*', '/', '%', '^', '+=', '-=', '*=', '/=', '++', '--', '==', '>', '>=', '<', '<=']
        operators.sort(key = len, reverse=True)
        operatorLoc, operatorType = CodeSpliter.string_contain_strings(
            chunk, operators)
        if operatorLoc != -1 and len(operatorType) != len(chunk):
            if len(chunk[0:operatorLoc]) != 0:
                chunks.append(CodeSpliter.split_on_operators(chunk[0:operatorLoc], chunks))
            operator = CodeSpliter.split_on_operators(chunk[operatorLoc:operatorLoc + len(operatorType)], chunks)
            if operator == ':=':
                operator = '='
            chunks.append(operator)
            return CodeSpliter.split_on_operators(chunk[operatorLoc + len(operatorType):], chunks)
        else:
            if chunk == ':=':
                chunk = '='
            return chunk
        
    @staticmethod
    def get_next_char_pos(string, pos, char = '\n'):
        while pos < len(string) and string[pos] != char:
            pos += 1
        return pos