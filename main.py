import os
import json
from lexer.lexer import lexer
from utils.helpers import read_file
from parser.parser import Parser
from analisador_semantico.semantic import SemanticAnalyzer
from tradutor.ctranslator import GtkTranslator 

def process_test_files():
    test_dir = "testes"
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

            print("\nExecutando Análise Semântica...")
            semantic_analyzer = SemanticAnalyzer()   
            try:
                symbol_table = semantic_analyzer.analyze(ast)
                print("Análise semântica concluída com sucesso!")

                print("\nTabela de símbolos gerada:")
                print(json.dumps(symbol_table, indent=4))

                print("\nGerando código GTK...")
                gtk_translator = GtkTranslator(symbol_table)
                gtk_code = gtk_translator.translate()
                
                gtk_output_file = f'output-{test_file}.c'
                with open(gtk_output_file, 'w') as f:
                    f.write(gtk_code)
                
                print(f"Código GTK gerado e salvo em {gtk_output_file}")
                
                compile_command = f"gcc `pkg-config --cflags gtk+-3.0` -o {test_file.replace('.simpleui', '')} {gtk_output_file} `pkg-config --libs gtk+-3.0`"
                print("\nPara compilar o código gerado, execute:")
                print(compile_command)
                
                with open(f'symbol_table-{test_file}.json', 'w') as f:
                    json.dump(symbol_table, f, indent=4)
                
            except ValueError as ve:
                print(f"Erro semântico ao processar {test_file}: {ve}")
            
        except SyntaxError as e:
            print(f"Erro de sintaxe ao processar {test_file}: {e}")

if __name__ == '__main__':
    process_test_files()