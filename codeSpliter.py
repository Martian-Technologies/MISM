class CodeSpliter:
    @staticmethod
    def split(code, splitTypes = {";"}):
        print("splitting\n",code)
        lines = CodeSpliter.splitOnTypesAndStuff(code, splitTypes)
        chunks = CodeSpliter.splitChunks(lines)
        return chunks
        
    @staticmethod
    def splitOnTypesAndStuff(code, splitTypes):
        lines = []
        line = ""
        i = 0
        while i < len(code):
            char = code[i]
            if char in splitTypes:
                if not (CodeSpliter.ifOnlyHas(line, {" "}) or len(line) == 0):
                    lines.append(line)
                line = ""
            elif char == "{":
                i, line = CodeSpliter.getBraceBlock(i, line, code)
                lines.append(line)
                line = ""
            elif char == "(":
                i, line = CodeSpliter.getBraceBlock(i, line, code, "(", ")")
            elif char == "/" and i+1 < len(code):
                if code[i+1] == "/":
                    i = CodeSpliter.getNextCharPos(code, i)
            elif char != "\n" and (len(line) > 0 or char != " "):
                
                line += char
            i += 1
        if len(line) != 0:
            raise Exception(f'statement {line} {i} need to end with one of these chars {splitTypes}')
        return lines
    
    @staticmethod
    def splitChunks(lines):
        allChucks = []
        for line in lines:
            chunks = []
            chunk = ""
            i = 0
            while i < len(line):
                char = line[i]
                if char == "{":
                    if not (CodeSpliter.ifOnlyHas(chunk, {" "}) or len(chunk) == 0):
                        chunks.append(chunk)
                    i, block = CodeSpliter.getBraceBlock(i, "", line, includeBrace=False)
                    chunk = CodeSpliter.split(block)
                    chunks.append(chunk)
                    chunk = ""
                elif char == "(":
                    if not (CodeSpliter.ifOnlyHas(chunk, {" "}) or len(chunk) == 0):
                        chunks.append(chunk)
                    i, block = CodeSpliter.getBraceBlock(i, "", line, "(", ")", False)
                    block += ";"
                    chunk = CodeSpliter.split(block, {";", ","})
                    chunks.append(chunk)
                    chunk = ""
                elif char == " ":
                    if not (CodeSpliter.ifOnlyHas(chunk, {" "}) or len(chunk) == 0):
                        chunk = CodeSpliter.splitOnOperators(chunk, chunks)
                        if len(chunk) != 0:
                            chunks.append(chunk)
                    chunk = ""
                else:
                    chunk += char
                i += 1
            if not (CodeSpliter.ifOnlyHas(chunk, {" "}) or len(chunk) == 0):
                chunk = CodeSpliter.splitOnOperators(chunk, chunks)
                if len(chunk) != 0:
                    chunks.append(chunk)
            allChucks.append(chunks)
        return allChucks
    
    @staticmethod
    def ifOnlyHas(string, chars):
        for char in string:
            if not char in chars:
                return False
        return True
    
    @staticmethod
    def getBraceBlock(start, line, code, braceOpen = "{", braceClose = "}", includeBrace = True):
        if includeBrace:
            line += braceOpen
        braceCounter = 1
        while braceCounter > 0:
            start += 1
            if start >= len(code):
                raise Exception(f"did not close curly brace type {braceOpen}{braceClose}")
            char = code[start]
            if char == braceOpen:
                braceCounter += 1
            elif char == braceClose:
                braceCounter -= 1
            if(char != "\n"):
                if includeBrace or braceCounter > 0:
                    line += char
        return start, line
    
    @staticmethod
    def stringContainStrings(string, strings):
        for s in strings:
            i = string.find(s)
            if i != -1:
                return i, s
        return -1, ""
    
    @staticmethod
    def splitOnOperators(chunk, chunks):
        operator = ["=", ":=", "+", "-", "*", "/", "+=", "-=", "*=", "/=", "++", "--", "==", ">", ">=", "<", "<="]
        operator.sort(key = len, reverse=True)
        operatorLoc, operatorType = CodeSpliter.stringContainStrings(
            chunk, operator)
        if operatorLoc != -1 and len(operatorType) != len(chunk):
            if len(chunk[0:operatorLoc]) != 0:
                chunks.append(CodeSpliter.splitOnOperators(chunk[0:operatorLoc], chunks))
            chunks.append(CodeSpliter.splitOnOperators(chunk[operatorLoc:operatorLoc + len(operatorType)], chunks))
            return CodeSpliter.splitOnOperators(chunk[operatorLoc + len(operatorType):], chunks)
        else:
            return chunk
        
    @staticmethod
    def getNextCharPos(string, pos, char = "\n"):
        while pos < len(string) and string[pos] != char:
            pos += 1
        return pos