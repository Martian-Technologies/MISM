class VariableNameGenerator:
    nameIndex = 0
    
    @staticmethod
    def gen_name(nameStart = 'none'):
        VariableNameGenerator.nameIndex += 1
        return f"{nameStart}, computer generated name, random shit:⭳ⲼⱢ╴⾈⿗⦷ⲟ {VariableNameGenerator.nameIndex}"

if __name__ == "__main__":
    print(VariableNameGenerator.gen_name())