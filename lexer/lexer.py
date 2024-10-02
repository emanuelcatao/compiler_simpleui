import re
from my_token import TokenClass, Token

def lexer(code):
    tokens = []
    linhas = code.split('\n')
    numero_da_linha = 1

    for linha in linhas:
        linha = re.sub(r'\s+', ' ', linha.strip())
        coluna = 1

        while linha:
            match = None
            for token_class in TokenClass:
                regex = token_class.value
                match = re.match(regex, linha)
                if match:
                    lexema = match.group(0)
                    if token_class not in (TokenClass.ESPACO_EM_BRANCO, TokenClass.COMENTARIO):
                        token = Token(token_class, lexema, numero_da_linha, coluna)
                        tokens.append(token)
                    linha = linha[len(lexema):].lstrip()
                    coluna += len(lexema)
                    break
            
            if match is None:
                raise SyntaxError(f"Erro léxico na linha {numero_da_linha}, coluna {coluna}: caractere inesperado: {linha[0]!r}")
        
        numero_da_linha += 1
    
    return tokens
