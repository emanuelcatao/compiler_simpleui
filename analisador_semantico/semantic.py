import json


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.window_created = False
        self.errors = []

    def analyze(self, ast):
        if ast["type"] != "Program":
            self.errors.append(
                "AST inválida: o nó raiz deve ser do tipo 'Program'.")
            return self.symbol_table

        for statement in ast["body"]:
            self.analyze_statement(statement)

        if not self.window_created:
            self.errors.append(
                "Erro semântico: nenhuma janela foi criada no programa.")

        return self.symbol_table

    def analyze_statement(self, statement):
        statement_type = statement["type"]

        if statement_type == "createWindow":
            self.analyze_create_window(statement)
        elif statement_type == "addElement":
            self.analyze_add_element(statement)
        elif statement_type == "variable_assignment":
            self.analyze_variable_assignment(statement)
        elif statement_type == "onKeypress":
            self.analyze_on_keypress(statement)
        elif statement_type == "onClick":
            self.analyze_on_click(statement)
        else:
            self.errors.append(
                f"Tipo de declaração desconhecido: {statement_type}")

    def analyze_create_window(self, statement):
        if self.window_created:
            self.errors.append(
                "Erro semântico: mais de uma janela foi criada.")
            return

        attributes = statement["attributes"]
        if "width" not in attributes or "height" not in attributes:
            self.errors.append(
                "Erro semântico: 'createWindow' deve especificar 'width' e 'height'.")
            return

        width = attributes["width"]
        height = attributes["height"]

        if not isinstance(width, int) or not isinstance(height, int):
            self.errors.append(
                "Erro semântico: 'width' e 'height' devem ser números inteiros.")
        elif width <= 0 or height <= 0:
            self.errors.append(
                "Erro semântico: 'width' e 'height' devem ser positivos.")
        else:
            self.window_created = True

    def analyze_on_keypress(self, statement):
        if not self.window_created:
            self.errors.append(
                "Erro semântico: 'onKeypress' declarado antes da criação da janela.")
            return

        key = statement["key"]
        if not isinstance(key, str):
            self.errors.append(
                "Erro semântico: a tecla em 'onKeypress' deve ser uma string.")
            return

        for action in statement["actions"]:
            self.analyze_action(action)


    def analyze_action(self, action):
        action_type = action["type"]

        if action_type == "shiftElement":
            element_id = action["element_id"].strip("\"")
            if element_id not in self.symbol_table:
                self.errors.append(f"Erro semântico: o elemento '{
                                   element_id}' não foi declarado.")
            x = action["x"]
            y = action["y"]
            if not isinstance(x, int) or not isinstance(y, int):
                self.errors.append(
                    f"Erro semântico: 'x' e 'y' em 'shiftElement' devem ser inteiros.")
        else:
            self.errors.append(
                f"Erro semântico: ação desconhecida '{action_type}'.")

    def analyze_add_element(self, statement):
        attributes = statement["attributes"]

        if "type" not in attributes or "x" not in attributes or "y" not in attributes:
            self.errors.append("Erro semântico: 'addElement' deve especificar 'type', 'x' e 'y'.")
            return

        element_type = attributes["type"].strip("\"")
        x = attributes["x"]
        y = attributes["y"]
        element_id = attributes.get("id", "").strip("\"")

        if not isinstance(x, int) or not isinstance(y, int):
            self.errors.append("Erro semântico: 'x' e 'y' devem ser números inteiros.")
        if element_id and element_id in self.symbol_table:
            self.errors.append(f"Erro semântico: o elemento '{element_id}' já foi declarado.")
        else:
            if element_id:
                self.symbol_table[element_id] = {"type": element_type, "attributes": attributes}

    def analyze_variable_assignment(self, statement):
        var_name = statement["name"]
        var_value = statement["value"]

        if var_value["type"] == "function_call":
            self.analyze_function_call(var_value)
        elif var_name in self.symbol_table:
            self.errors.append(f"Erro semântico: a variável '{var_name}' já foi declarada.")
        elif var_value["type"] not in ["string", "number"]:
            self.errors.append(f"Erro semântico: tipo inválido para a variável '{var_name}'.")
        else:
            self.symbol_table[var_name] = {"type": var_value["type"], "value": var_value["value"]}

    def analyze_on_click(self, statement):
        target = statement["target"].strip("\"")
        if target not in self.symbol_table:
            self.errors.append(f"Erro semântico: o botão '{target}' não foi declarado.")
            return

        for action in statement["actions"]:
            action_type = action["type"]
            if action_type == "variable_assignment":
                self.analyze_variable_assignment(action)
            elif action_type == "setProperty":
                self.analyze_set_property(action)
            else:
                self.errors.append(f"Erro semântico: ação desconhecida '{action_type}'.")

    def analyze_set_property(self, statement):
        element_id = statement["element_id"].strip("\"")
        if element_id not in self.symbol_table:
            self.errors.append(f"Erro semântico: o elemento '{element_id}' não foi declarado.")
        # Adicionar verificações adicionais se necessário para a expressão

    def analyze_function_call(self, function_call):
        function_name = function_call["name"]
        if function_name not in ["getProperty"]:
            self.errors.append(f"Erro semântico: função desconhecida '{function_name}'.")

        arguments = function_call["arguments"]
        if len(arguments) < 2:
            self.errors.append(f"Erro semântico: número insuficiente de argumentos para a função '{function_name}'.")
        element_id = arguments[0].strip("\"")
        if element_id not in self.symbol_table:
            self.errors.append(f"Erro semântico: o elemento '{element_id}' não foi declarado.")

    def report_errors(self):
        if self.errors:
            print("Erros semânticos encontrados:")
            for error in self.errors:
                print(f"- {error}")
        else:
            print("Análise semântica concluída sem erros.")

def load_ast_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            ast = json.load(file)
        return ast
    except FileNotFoundError:
        print(f"Erro: Arquivo {file_path} não encontrado.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar o JSON: {e}")
    return None

# file_path = "../output-codigo_loop.simpleui.json"
# ast = load_ast_from_file(file_path)

# analyzer = SemanticAnalyzer()
# analyzer.analyze(ast)
# analyzer.report_errors()             