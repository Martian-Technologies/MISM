class VariableNameGenerator:
    nameIndex = 0
    
    @staticmethod
    def gen_name(nameStart = 'none'):
        VariableNameGenerator.nameIndex += 1
        return f"COMP_{nameStart}_{VariableNameGenerator.nameIndex}"
    
    returnNameID = 0
    
    @staticmethod
    def get_return_name(functionName):
        return f"return_{functionName}:{VariableNameGenerator.returnNameID}"
    
    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def isValidVarName(name):
        if VariableNameGenerator.is_number(name) or type(name) != str or name in ['+', '-', '*', '/', '%', '^']:
            return False
        return True
    
    functionID = 0
    @staticmethod
    def get_new_func_ID():
        VariableNameGenerator.functionID += 1
        return VariableNameGenerator.functionID-1
    
    def get_last_func_ID():
        return VariableNameGenerator.functionID-1

if __name__ == "__main__":
    print(VariableNameGenerator.gen_name())