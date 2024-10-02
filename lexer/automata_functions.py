from lexer.my_token import TokenClass
from lexer.automata import AFD

def create_automaton_palavra_reservada():
    afd = AFD()
    q0 = afd.add_state('q0', is_initial=True)
    reserved_words = ["let", "function", "if", "else", "repeat", "times", "loop", "every", "ms", "createWindow",
                      "addElement", "moveElement", "shiftElement", "showElement", "hideElement", "onKeypress",
                      "onClick", "getProperty", "setProperty"]

    for word in reserved_words:
        current_state = q0
        for i, c in enumerate(word):
            next_state_name = f"q_{word}_{i+1}"
            next_state = None
            for state in afd.states:
                if state.name == next_state_name:
                    next_state = state
                    break
            if next_state is None:
                is_final = (i == len(word) - 1)
                next_state = afd.add_state(next_state_name, is_final=is_final)
            afd.add_transition(current_state, next_state, c)
            current_state = next_state

    return afd

def create_automaton_operador():
    afd = AFD()
    q0 = afd.add_state('q0', is_initial=True)

    operators = {
        '+': 'q_plus',
        '-': 'q_minus',
        '*': 'q_mul',
        '/': 'q_div',
        '=': 'q_eq',
        '<': 'q_lt',
        '>': 'q_gt',
    }

    for symbol, state_name in operators.items():
        state = afd.add_state(state_name, is_final=True)
        afd.add_transition(q0, state, symbol)

    q_lt_eq = afd.add_state('q_lt_eq', is_final=True)
    afd.add_transition(afd.states_by_name('q_lt'), q_lt_eq, '=')

    q_gt_eq = afd.add_state('q_gt_eq', is_final=True)
    afd.add_transition(afd.states_by_name('q_gt'), q_gt_eq, '=')

    q_plus_eq = afd.add_state('q_plus_eq', is_final=True)
    afd.add_transition(afd.states_by_name('q_plus'), q_plus_eq, '=')

    q_minus_eq = afd.add_state('q_minus_eq', is_final=True)
    afd.add_transition(afd.states_by_name('q_minus'), q_minus_eq, '=')

    q_plus_plus = afd.add_state('q_plus_plus', is_final=True)
    afd.add_transition(afd.states_by_name('q_plus'), q_plus_plus, '+')

    q_minus_minus = afd.add_state('q_minus_minus', is_final=True)
    afd.add_transition(afd.states_by_name('q_minus'), q_minus_minus, '-')

    #afd.plot("operador")

    return afd

def create_automaton_delimitador():
    afd = AFD()
    q0 = afd.add_state('q0', is_initial=True)
    q_final = afd.add_state('q_final', is_final=True)
    delimiters = [',', ';', '(', ')', '.', '{', '}']

    for delim in delimiters:
        afd.add_transition(q0, q_final, delim)

    return afd

def create_automaton_identificador():
    afd = AFD()
    q0 = afd.add_state('q0', is_initial=True)
    q1 = afd.add_state('q1', is_final=True)

    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    letters_digits = letters + '0123456789'

    for c in letters:
        afd.add_transition(q0, q1, c)

    for c in letters_digits:
        afd.add_transition(q1, q1, c)

    return afd

def create_automaton_numero():
    afd = AFD()
    q0 = afd.add_state('q0', is_initial=True)
    q_int = afd.add_state('q_int', is_final=True)
    q_dot = afd.add_state('q_dot')
    q_frac = afd.add_state('q_frac', is_final=True)

    digits = '0123456789'

    for d in digits:
        afd.add_transition(q0, q_int, d)
        afd.add_transition(q_int, q_int, d)

    afd.add_transition(q_int, q_dot, '.')

    for d in digits:
        afd.add_transition(q_dot, q_frac, d)
        afd.add_transition(q_frac, q_frac, d)

    return afd

def create_automaton_comentario():
    afd = AFD()
    q0 = afd.add_state('q0', is_initial=True)
    q_hash1 = afd.add_state('q_hash1')
    q_hash2 = afd.add_state('q_hash2', is_final=True)
    q_comment = afd.add_state('q_comment', is_final=True)

    afd.add_transition(q0, q_hash1, '#')
    afd.add_transition(q_hash1, q_hash2, '#')

    # Qualquer caractere depois de '##' é parte do comentário
    for i in range(32, 127):  # tabela ASCII
        c = chr(i)
        afd.add_transition(q_hash2, q_comment, c)
        afd.add_transition(q_comment, q_comment, c)

    #for i in range(128, 255):  
    #    c = bytes([i]).decode('cp437')
    #    afd.add_transition(q_hash2, q_comment, c)
    #    afd.add_transition(q_comment, q_comment, c)

    afd.add_transition(q_hash2, q_comment, ' ')
    afd.add_transition(q_comment, q_comment, ' ')

    #afd.plot("comentario")

    return afd

def create_automaton_espaco_em_branco():
    afd = AFD()
    q0 = afd.add_state('q0', is_initial=True)
    q_space = afd.add_state('q_space', is_final=True)

    whitespace_chars = [' ', '\t', '\n', '\r']

    for c in whitespace_chars:
        afd.add_transition(q0, q_space, c)
        afd.add_transition(q_space, q_space, c)

    #afd.plot("em_branco")

    return afd

def create_automaton_string():
    afd = AFD()
    q0 = afd.add_state('q0', is_initial=True)
    q_quote_start = afd.add_state('q_quote_start')
    q_content = afd.add_state('q_content')
    q_quote_end = afd.add_state('q_quote_end', is_final=True)

    afd.add_transition(q0, q_quote_start, '"')

    for i in range(32, 127):
        c = chr(i)
        if c != '"':
            afd.add_transition(q_quote_start, q_content, c)
            afd.add_transition(q_content, q_content, c)

    afd.add_transition(q_content, q_quote_end, '"')

    #afd.plot("string")

    return afd


automata_functions = {
    TokenClass.PALAVRA_RESERVADA: create_automaton_palavra_reservada,
    TokenClass.OPERADOR: create_automaton_operador,
    TokenClass.DELIMITADOR: create_automaton_delimitador,
    TokenClass.IDENTIFICADOR: create_automaton_identificador,
    TokenClass.NUMERO: create_automaton_numero,
    TokenClass.COMENTARIO: create_automaton_comentario,
    TokenClass.ESPACO_EM_BRANCO: create_automaton_espaco_em_branco,
    TokenClass.STRING: create_automaton_string,
}