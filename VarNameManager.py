class VariableNameManager:
    nameIndex = 0
    
    @staticmethod
    def gen_name(nameStart = 'none'):
        VariableNameManager.nameIndex += 1
        return f"COMP_{nameStart}_{VariableNameManager.nameIndex}"
    
    returnNameID = 0
    
    @staticmethod
    def get_return_name(functionName):
        return f"return_{functionName}:{VariableNameManager.returnNameID}"
    
    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def isValidVarName(name):
        if VariableNameManager.is_number(name) or type(name) != str or name in ['+', '-', '*', '/', '%', '^', '==', '>', '>=', '<', '<=']:
            return False
        return True
    
    functionID = 0
    @staticmethod
    def get_new_func_ID():
        VariableNameManager.functionID += 1
        return VariableNameManager.functionID-1
    
    def get_last_func_ID():
        return VariableNameManager.functionID-1
    
    @staticmethod
    def replace_var_names(code, start = '', deepScan = False):
        return VariableNameManager.scan_replace_var_names(code, start, deepScan)

    @staticmethod
    def scan_replace_var_names(code, start, deepScan):
        if type(code) == dict:
            i = 0
            while i < len(code.keys()):
                k = list(code.keys())[i]
                if ('expression' in k) or ('args' in k) or ('var' in k) or (k in ['init', 'increment', 'condition']):
                    code[k] = VariableNameManager.scan_replace_var_names(code[k], start, deepScan)
                elif deepScan:
                    if ('code' in k) or ('else' in k):
                        code[k] = VariableNameManager.scan_replace_var_names(code[k], start, deepScan)
                i+=1
        elif type(code) == list:
            i = 0
            while i < len(code):
                code[i] = VariableNameManager.scan_replace_var_names(code[i], start, deepScan)
                i += 1
        else:
            if VariableNameManager.isValidVarName(code):
                code = f"{start}_{code}"
        return code

if __name__ == "__main__":
    print(VariableNameManager.gen_name())