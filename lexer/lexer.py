import re
from lexer.my_token import TokenClass, Token
from lexer.automata_functions import automata_functions

def lexer(code):
    tokens = []
    position = 0
    length = len(code)

    current_line = 1
    current_column = 1
    
    while position < length:
        match_found = False
        for token_class, automaton_function in automata_functions.items():
            afd = automaton_function()
            current_state = afd.initial_state
            lookahead = position
            last_accepting_position = None
            last_accepting_state = None

            token_start_line = current_line
            token_start_column = current_column

            if code[position] == '-' and position + 1 < length and code[position + 1].isdigit():
                lookahead += 1
                while lookahead < length and code[lookahead].isdigit():
                    lookahead += 1
                lexeme = code[position:lookahead]
                tokens.append(Token(TokenClass.NUMERO, lexeme, token_start_line, token_start_column))
                position = lookahead
                match_found = True
                break

            while lookahead < length:
                symbol = code[lookahead]

                next_state = None
                if current_state in afd.transitions:
                    for transicao in afd.transitions[current_state]:
                        if transicao.symbol == symbol:
                            next_state = transicao.destine
                            break
                if next_state is None:
                    break
                current_state = next_state
                lookahead += 1

                if symbol == '\n':
                    current_line += 1
                    current_column = 1
                else:
                    current_column += 1

                if current_state.is_final:
                    last_accepting_position = lookahead
                    last_accepting_state = current_state

            if last_accepting_state is not None:
                lexeme = code[position:last_accepting_position]
                if token_class not in (TokenClass.ESPACO_EM_BRANCO, TokenClass.COMENTARIO):
                    token = Token(token_class, lexeme, token_start_line, token_start_column)
                    tokens.append(token)

                position = last_accepting_position
                match_found = True
                break

        if not match_found:
            error_line = current_line
            error_column = current_column
            raise SyntaxError(f"Erro léxico na linha {error_line}, coluna {error_column}: caractere inesperado: {code[position]!r}")
    
    return tokens

