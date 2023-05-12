from rply import LexerGenerator

class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()
    
    def _add_tokens(self):
        self.lexer.add('PRINT', r'print')
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')
        self.lexer.add('SEMI_COLON', r'\;')
        self.lexer.add('NUMBER', r'\d+')
        self.lexer.add('SUM', r'\+')
        self.lexer.add('SUB', r'\-')
        self.lexer.add('MUL', r'\*')
        self.lexer.add('DIV', r'\/')
        self.lexer.add('MOD', r'\%')
        self.lexer.add('POW', r'\^')
        self.lexer.add('EQUALS', r'\=\=')
        self.lexer.add('ASSIGN', r'\=')
        self.lexer.add('VAR', r'var')
        self.lexer.add('IF', r'if')
        self.lexer.add('ELSE', r'else')
        self.lexer.add('ELIF', r'elif')
        self.lexer.add('WHILE', r'while')
        self.lexer.add('FOR', r'for')
        self.lexer.add('IN', r'in')
        self.lexer.add('DO', r'do')
        self.lexer.add('LESS_THAN', r'\<')
        self.lexer.add('GREATER_THAN', r'\>')
        self.lexer.add('LESS_THAN_EQUAL', r'\<\=')
        self.lexer.add('GREATER_THAN_EQUAL', r'\>\=')
        self.lexer.add('NOT_EQUAL', r'\!\=')
        self.lexer.add('AND', r'\&\&')
        self.lexer.add('OR', r'\|\|')
        self.lexer.add('NOT', r'\!')
        self.lexer.add('COMMA', r'\,')

        self.lexer.ignore('\s+') # ignore spaces
    
    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()

