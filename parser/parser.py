from lexer.my_token import TokenClass
from graphviz import Digraph
import uuid

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[0]

        # Mapeamento de palavras reservadas para métodos de parsing correspondentes
        self.parse_map = {
            "createWindow": self.parse_create_window,
            "addElement": self.parse_add_element,
            "onClick": self.parse_on_click,
            "setProperty": self.parse_set_property,
            "let": self.parse_variable_assignment,
            "showElement": self.parse_show_element,
            "hideElement": self.parse_hide_element,
            "moveElement": self.parse_move_element,
            "shiftElement": self.parse_shift_element,
            "getProperty": self.parse_get_property,
            "onKeypress": self.parse_on_keypress,
        }

    def advance(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None

    def expect(self, token_class, token_value=None):
        if (self.current_token is not None and 
            self.current_token.token_class == token_class and 
            (token_value is None or self.current_token.token_value == token_value)):
            self.advance()
        else:
            raise SyntaxError(
                f"Esperado um token {token_class}{' com valor ' + token_value if token_value else ''}, "
                f"mas encontrado {self.current_token}"
            )

    def parse(self):
        """Faz o parse de uma lista de tokens e constrói a AST."""
        instructions = []
        while self.current_token is not None:
            instruction = self.parse_instruction()
            if instruction is not None:
                instructions.append(instruction)
        return {"type": "Program", "body": instructions}

    def parse_instruction(self):
        """Direciona para o parser adequado com base no token atual."""
        token_value = self.current_token.token_value
        if token_value in self.parse_map:
            return self.parse_map[token_value]()
        else:
            raise SyntaxError(f"Token inesperado {token_value} na instrução")

    def parse_create_window(self):
        self.expect(TokenClass.PALAVRA_RESERVADA, "createWindow")
        self.expect(TokenClass.DELIMITADOR, "(")

        title = self.current_token.token_value
        self.expect(TokenClass.STRING)
        
        self.expect(TokenClass.DELIMITADOR, ",")
        self.expect(TokenClass.IDENTIFICADOR, "width")
        self.expect(TokenClass.OPERADOR, "=")
        width = int(self.current_token.token_value)
        self.expect(TokenClass.NUMERO)

        self.expect(TokenClass.DELIMITADOR, ",")
        self.expect(TokenClass.IDENTIFICADOR, "height")
        self.expect(TokenClass.OPERADOR, "=")
        height = int(self.current_token.token_value)
        self.expect(TokenClass.NUMERO)

        self.expect(TokenClass.DELIMITADOR, ")")
        self.expect(TokenClass.DELIMITADOR, ";")

        return {
            "type": "createWindow",
            "attributes": {
                "title": title,
                "width": width,
                "height": height
            }
        }

    def parse_add_element(self):
        self.expect(TokenClass.PALAVRA_RESERVADA, "addElement")
        self.expect(TokenClass.DELIMITADOR, "(")

        element_data = {}

        while self.current_token.token_class == TokenClass.IDENTIFICADOR:
            key = self.current_token.token_value
            self.advance()
            self.expect(TokenClass.OPERADOR, "=")
            
            # Check for type of value
            if self.current_token.token_class == TokenClass.STRING:
                element_data[key] = self.current_token.token_value
                self.expect(TokenClass.STRING)
            elif self.current_token.token_class == TokenClass.NUMERO:
                element_data[key] = int(self.current_token.token_value)
                self.expect(TokenClass.NUMERO)
            
            if self.current_token.token_value == ",":
                self.advance()
            else:
                break

        self.expect(TokenClass.DELIMITADOR, ")")
        self.expect(TokenClass.DELIMITADOR, ";")

        return {"type": "addElement", "attributes": element_data}

    def parse_set_property(self):
        self.expect(TokenClass.IDENTIFICADOR, "setProperty")
        self.expect(TokenClass.DELIMITADOR, "(")

        element_id = self.current_token.token_value
        self.expect(TokenClass.STRING)

        self.expect(TokenClass.DELIMITADOR, ",")
        self.expect(TokenClass.IDENTIFICADOR, "text")
        self.expect(TokenClass.OPERADOR, "=")

        expression = self.parse_expression_list()
        self.expect(TokenClass.DELIMITADOR, ")")
        self.expect(TokenClass.DELIMITADOR, ";")
        
        return {"type": "setProperty", "element_id": element_id, "expression": expression}

    def parse_variable_assignment(self):
        """Parse de variável de atribuição."""
        self.expect(TokenClass.PALAVRA_RESERVADA, "let")
        var_name = self.current_token.token_value
        self.expect(TokenClass.IDENTIFICADOR)
        
        self.expect(TokenClass.OPERADOR, "=")
        
        value = self.parse_expression()
        
        self.expect(TokenClass.DELIMITADOR, ";")
        
        return {"type": "variable_assignment", "name": var_name, "value": value}

    def parse_expression(self):
        """Parse uma expressão, que pode ser um número, string, identificador ou chamada de função."""
        if self.current_token.token_class == TokenClass.PALAVRA_RESERVADA:
            return self.parse_function_call()
        elif self.current_token.token_class == TokenClass.IDENTIFICADOR:
            var_name = self.current_token.token_value
            self.advance()
            return {"type": "identifier", "name": var_name}
        elif self.current_token.token_class == TokenClass.NUMERO:
            num_value = int(self.current_token.token_value)
            self.advance()
            return {"type": "number", "value": num_value}
        elif self.current_token.token_class == TokenClass.STRING:
            str_value = self.current_token.token_value
            self.advance()
            return {"type": "string", "value": str_value}
        else:
            raise SyntaxError(f"Token inesperado na expressão: {self.current_token.token_value}")

    def parse_function_call(self):
        func_name = self.current_token.token_value
        self.advance()
        self.expect(TokenClass.DELIMITADOR, "(")
        args = []
        while self.current_token and self.current_token.token_value != ")":
            args.append(self.current_token.token_value)
            self.advance()
            if self.current_token.token_value == ",":
                self.advance()
        self.expect(TokenClass.DELIMITADOR, ")")
        return {"type": "function_call", "name": func_name, "arguments": args}

    def parse_show_element(self):
        self.expect(TokenClass.PALAVRA_RESERVADA, "showElement")
        self.expect(TokenClass.DELIMITADOR, "(")
        element_id = self.current_token.token_value
        self.expect(TokenClass.STRING)
        self.expect(TokenClass.DELIMITADOR, ")")
        self.expect(TokenClass.DELIMITADOR, ";")
        return {"type": "showElement", "element_id": element_id}

    def parse_hide_element(self):
        self.expect(TokenClass.PALAVRA_RESERVADA, "hideElement")
        self.expect(TokenClass.DELIMITADOR, "(")
        element_id = self.current_token.token_value
        self.expect(TokenClass.STRING)
        self.expect(TokenClass.DELIMITADOR, ")")
        self.expect(TokenClass.DELIMITADOR, ";")
        return {"type": "hideElement", "element_id": element_id}

    def parse_move_element(self):
        self.expect(TokenClass.PALAVRA_RESERVADA, "moveElement")
        self.expect(TokenClass.DELIMITADOR, "(")
        element_id = self.current_token.token_value
        self.expect(TokenClass.STRING)
        self.expect(TokenClass.DELIMITADOR, ",")
        self.expect(TokenClass.IDENTIFICADOR, "x")
        self.expect(TokenClass.OPERADOR, "=")
        x = int(self.current_token.token_value)
        self.expect(TokenClass.NUMERO)
        self.expect(TokenClass.DELIMITADOR, ",")
        self.expect(TokenClass.IDENTIFICADOR, "y")
        self.expect(TokenClass.OPERADOR, "=")
        y = int(self.current_token.token_value)
        self.expect(TokenClass.NUMERO)
        self.expect(TokenClass.DELIMITADOR, ")")
        self.expect(TokenClass.DELIMITADOR, ";")
        return {"type": "moveElement", "element_id": element_id, "x": x, "y": y}

    def parse_shift_element(self):
        self.expect(TokenClass.PALAVRA_RESERVADA, "shiftElement")
        self.expect(TokenClass.DELIMITADOR, "(")
        element_id = self.current_token.token_value
        self.expect(TokenClass.STRING)
        self.expect(TokenClass.DELIMITADOR, ",")
        self.expect(TokenClass.IDENTIFICADOR, "x")
        self.expect(TokenClass.OPERADOR, "=")
        x = int(self.current_token.token_value)
        self.expect(TokenClass.NUMERO)
        self.expect(TokenClass.DELIMITADOR, ",")
        self.expect(TokenClass.IDENTIFICADOR, "y")
        self.expect(TokenClass.OPERADOR, "=")
        y = int(self.current_token.token_value)
        self.expect(TokenClass.NUMERO)
        self.expect(TokenClass.DELIMITADOR, ")")
        self.expect(TokenClass.DELIMITADOR, ";")
        return {"type": "shiftElement", "element_id": element_id, "x": x, "y": y}

    def parse_get_property(self):
        self.expect(TokenClass.PALAVRA_RESERVADA, "getProperty")
        self.expect(TokenClass.DELIMITADOR, "(")
        element_id = self.current_token.token_value
        self.expect(TokenClass.STRING)
        self.expect(TokenClass.DELIMITADOR, ",")
        self.expect(TokenClass.IDENTIFICADOR, "value")
        self.expect(TokenClass.DELIMITADOR, ")")
        return {"type": "getProperty", "element_id": element_id, "property": "value"}

    def parse_on_click(self):
        self.expect(TokenClass.IDENTIFICADOR, "onClick")
        self.expect(TokenClass.DELIMITADOR, "(")
        target = self.current_token.token_value
        self.expect(TokenClass.STRING)
        self.expect(TokenClass.DELIMITADOR, ")")
        self.expect(TokenClass.DELIMITADOR, "{")
        actions = self.parse_actions_block()
        self.expect(TokenClass.DELIMITADOR, "}")
        return {"type": "onClick", "target": target, "actions": actions}

    def parse_on_keypress(self):
        self.expect(TokenClass.PALAVRA_RESERVADA, "onKeypress")
        self.expect(TokenClass.DELIMITADOR, "(")
        key = self.current_token.token_value
        self.expect(TokenClass.STRING)
        self.expect(TokenClass.DELIMITADOR, ")")
        self.expect(TokenClass.DELIMITADOR, "{")
        actions = self.parse_actions_block()
        self.expect(TokenClass.DELIMITADOR, "}")
        return {"type": "onKeypress", "key": key, "actions": actions}

    def parse_actions_block(self):
        actions = []
        while self.current_token and self.current_token.token_value != '}':
            action = self.parse_action()
            if action is not None:
                actions.append(action)
        return actions

    def parse_action(self):
        token_value = self.current_token.token_value
        if token_value in self.parse_map:
            return self.parse_map[token_value]()
        elif token_value == ";":
            self.advance()
            return None
        else:
            raise SyntaxError(f"Token inesperado {token_value} no bloco de ações")

    def parse_expression_list(self):
        expression = []
        while self.current_token.token_class in (TokenClass.STRING, TokenClass.IDENTIFICADOR, TokenClass.OPERADOR):
            expression.append(self.current_token.token_value)
            self.advance()
        return expression

    def display_ast(self, ast):
        print(json.dumps(ast, indent=4))

    def generate_ast_graph(self, ast, filename="ast"):
        """Gera um gráfico visual da AST e salva como uma imagem."""
        dot = Digraph(comment='AST')
        
        def add_nodes_recursive(node, parent_id=None):
            node_id = str(uuid.uuid4())
            if isinstance(node, dict):
                label = node.get("type", "node")
                dot.node(node_id, label)
                if parent_id:
                    dot.edge(parent_id, node_id)
                for key, child in node.items():
                    if key != "type":  # Evita redundância no rótulo
                        add_nodes_recursive(child, node_id)
            elif isinstance(node, list):
                list_id = str(uuid.uuid4())
                dot.node(list_id, "List")
                if parent_id:
                    dot.edge(parent_id, list_id)
                for item in node:
                    add_nodes_recursive(item, list_id)
            else:
                dot.node(node_id, str(node))
                if parent_id:
                    dot.edge(parent_id, node_id)

        add_nodes_recursive(ast)
        dot.render(filename, format='png')
        print(f"AST visual salva como {filename}.png")
