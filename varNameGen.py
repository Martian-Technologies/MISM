class VariableNameGenerator:
    nameIndex = 0
    
    @staticmethod
    def gen_name(nameStart = 'none'):
        VariableNameGenerator.nameIndex += 1
        return f"{nameStart}_computer_generated_name_random_shit:⭳ⲼⱢ╴⾈⿗⦷ⲟ:_{VariableNameGenerator.nameIndex}"
    
    @staticmethod
    def get_return_name(functionName):
        return f"return_var_shit:⭳ⲼⱢ╴⾈⿗⦷ⲟ_func:_{functionName}"

if __name__ == "__main__":
    print(VariableNameGenerator.gen_name())