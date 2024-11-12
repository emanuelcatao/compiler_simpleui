import os
import json
from lexer.lexer import lexer
from utils.helpers import read_file
from parser.parser import Parser

def process_test_files():
    test_dir = "Testes"
    test_files = [f for f in os.listdir(test_dir) if f.endswith('.simpleui')]
    
    if not test_files:
        print("Nenhum arquivo de teste encontrado.")
        return
    
    for test_file in test_files:
        full_path = os.path.join(test_dir, test_file)
        print(f"\nProcessando arquivo: {test_file}")
        
        code = read_file(full_path)
        tokens = lexer(code)
        
        print("\nTokens gerados pelo lexer:")
        for token in tokens:
            print(f'{token.token_class.name:<20} {token.token_value:<20} (Linha: {token.line}, Coluna: {token.column})')
        
        parser = Parser(tokens)
        try:
            ast = parser.parse()
            print("\nAST gerada pelo parser:")
            print(json.dumps(ast, indent=4))
            
            output_filename = f"output-{test_file}"
            parser.generate_ast_graph(ast, output_filename)

            with open(f'output-{test_file}.json', 'w') as f:
                json.dump(ast, f, indent=4)

            
        except SyntaxError as e:
            print(f"Erro de sintaxe ao processar {test_file}: {e}")

if __name__ == '__main__':
    process_test_files()
