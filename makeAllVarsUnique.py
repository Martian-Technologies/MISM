from stackUtil import StackUtil

if __name__ == "__main__":
    import main

class MakeAllVarsUnique:
    @staticmethod
    def make_all_vars_unique(code):
        varUsages = StackUtil.get_var_usages(code)
        for var in varUsages:
            code = MakeAllVarsUnique.make_vars_unique(code, var, varUsages[var])
        return code
    
    varId = 0
    
    @staticmethod
    def make_vars_unique(code: list, var: str, varPaths: list):
        startVarPath:list = varPaths[0]['stack']
        sameVarPaths: list = []
        for path in varPaths:
            if not (StackUtil.get_path_relative(startVarPath, path['stack']) in ['same', 'p2 in p1']):
                for varPath in sameVarPaths:
                    code = StackUtil.follow_index_stack_set(code, varPath, f"id:_{MakeAllVarsUnique.varId}_" + var)
                MakeAllVarsUnique.varId += 1
                startVarPath = path['stack']
                sameVarPaths = []
            sameVarPaths.append(path['stack'])
        for varPath in sameVarPaths:
            for varPath in sameVarPaths:
                code = StackUtil.follow_index_stack_set(code, varPath, f"id:_{MakeAllVarsUnique.varId}_" + var)
            MakeAllVarsUnique.varId += 1
        return code