import os
from lexer.lexer import lexer
from utils.helpers import read_file

def process_test_files():
    test_dir = "Testes"
    
    test_files = [f for f in os.listdir(test_dir) if f.endswith('.simpleui')]
    
    if not test_files:
        return
    
    for test_file in test_files:
        full_path = os.path.join(test_dir, test_file)
        print(f"\nProcessando arquivo: {test_file}")
        
        code = read_file(full_path)

        tokens = lexer(code)
        
        with open(f'output-{test_file}.md', 'w') as f:
            f.write(f'| {"Classe do Token":<20} | {"Valor":<20} | {"Linha":<20} | {"Coluna":<20} |\n')
            f.write(f'| {"-"*20:<20} | {"-"*20:<20} | {"-"*20:<20} | {"-"*20:<20} |\n')

        for token in tokens:
            with open(f'output-{test_file}.md', 'a') as f:
                f.write(f'| {token.token_class.name:<20} | {token.token_value:<20} | {token.line:<20} | {token.column:<20} |\n')

if __name__ == '__main__':
    process_test_files()
