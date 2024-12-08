import json

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {"elements": {}, "events": {}, "variables": {}}
        self.window_created = False
        self.errors = []

    def analyze(self, ast):
        """Analisa o programa a partir do AST."""
        if ast["type"] != "Program":
            self.errors.append("AST inválida: o nó raiz deve ser do tipo 'Program'.")
            return self.symbol_table

        for statement in ast["body"]:
            self.analyze_statement(statement)

        if not self.window_created:
            self.errors.append("Erro semântico: nenhuma janela foi criada no programa.")

        return self.symbol_table

    def analyze_statement(self, statement):
        """Analisa cada declaração."""
        statement_type = statement["type"]

        if statement_type == "createWindow":
            self.analyze_create_window(statement)
        elif statement_type == "addElement":
            self.analyze_add_element(statement)
        elif statement_type == "variable_assignment":
            self.analyze_variable_assignment(statement)
        elif statement_type == "onClick":
            self.analyze_on_click(statement)
        elif statement_type == "onKeypress":
            self.analyze_on_keypress(statement)
        else:
            self.errors.append(f"Tipo de declaração desconhecido: {statement_type}")

    def analyze_create_window(self, statement):
        """Analisa a declaração de criação de janela."""
        if self.window_created:
            self.errors.append("Erro semântico: mais de uma janela foi criada.")
            return

        attributes = statement["attributes"]
        title = attributes.get("title", "Unnamed Window")
        width = attributes.get("width", 0)
        height = attributes.get("height", 0)

        if isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0:
            self.window_created = True
            self.symbol_table["window"] = {
                "title": title,
                "width": width,
                "height": height
            }
        else:
            self.errors.append(
                "Erro semântico: 'width' e 'height' devem ser números inteiros positivos.")

    def analyze_add_element(self, statement):
        """Analisa a adição de um elemento."""
        attributes = statement["attributes"]

        element_type = attributes.get("type", "").strip("\"")
        x = attributes.get("x")
        y = attributes.get("y")
        element_id = attributes.get("id", "").strip("\"")

        if not element_id and element_type == "button":
            element_id = f"button_{len(self.symbol_table['elements']) + 1}"

        if not element_type or x is None or y is None:
            self.errors.append("Erro semântico: 'addElement' deve especificar 'type', 'x' e 'y'.")
            return

        if not isinstance(x, int) or not isinstance(y, int):
            self.errors.append("Erro semântico: 'x' e 'y' devem ser números inteiros.")
            return

        if element_id in self.symbol_table["elements"]:
            self.errors.append(f"Erro semântico: o elemento '{element_id}' já foi declarado.")
        else:
            self.symbol_table["elements"][element_id] = {
                "type": element_type,
                "attributes": attributes,
                "actions": []
            }

    def analyze_variable_assignment(self, statement):
        """Analisa a atribuição de variável."""
        var_name = statement["name"]
        var_value = statement["value"]

        if var_value["type"] == "function_call":
            self.analyze_function_call(var_value)

        if var_value["type"] not in ["string", "number"]:
            self.errors.append(f"Erro semântico: tipo inválido para a variável '{var_name}'.")
        else:
            self.symbol_table["variables"][var_name] = {
                "type": var_value["type"],
                "value": var_value["value"]
            }

    def analyze_function_call(self, function_call):
        """Analisa chamadas de função."""
        function_name = function_call["name"]
        if function_name not in ["getProperty"]:
            self.errors.append(f"Erro semântico: função desconhecida '{function_name}'.")
            return

        arguments = function_call["arguments"]
        if len(arguments) < 2:
            self.errors.append(f"Erro semântico: número insuficiente de argumentos para '{function_name}'.")
            return

        element_id = arguments[0].strip("\"")
        if element_id not in self.symbol_table["elements"]:
            self.errors.append(f"Erro semântico: o elemento '{element_id}' não foi declarado.")

    def analyze_on_click(self, statement):
        """Analisa eventos onClick."""
        target = statement["target"].strip("\"")
        
        if target == "button":
            button_elements = [
                btn_id for btn_id, btn_info in self.symbol_table["elements"].items() 
                if btn_info["type"] == "button"
            ]
            if not button_elements:
                self.errors.append(f"Erro semântico: nenhum botão foi declarado.")
                return
            target = button_elements[0]

        if target not in self.symbol_table["elements"]:
            self.errors.append(f"Erro semântico: o botão '{target}' não foi declarado.")
            return

        if "events" not in self.symbol_table:
            self.symbol_table["events"] = {}

        if target not in self.symbol_table["events"]:
            self.symbol_table["events"][target] = {
                "type": "onClick",
                "actions": []
            }

        for action in statement["actions"]:
            self.analyze_action(action)
            self.symbol_table["events"][target]["actions"].append(action)

    def analyze_on_keypress(self, statement):
        """Analisa eventos onKeypress."""
        key = statement["key"].strip("\"")
        
        if "events" not in self.symbol_table:
            self.symbol_table["events"] = {}

        if "keypress" not in self.symbol_table["events"]:
            self.symbol_table["events"]["keypress"] = {}

        if key not in self.symbol_table["events"]["keypress"]:
            self.symbol_table["events"]["keypress"][key] = {
                "type": "onKeypress",
                "actions": []
            }

        for action in statement["actions"]:
            self.analyze_action(action)
            self.symbol_table["events"]["keypress"][key]["actions"].append(action)

    def analyze_action(self, action):
        """Analisa ações dentro de eventos."""
        action_type = action["type"]

        if action_type == "setProperty":
            self.analyze_set_property(action)
        elif action_type == "variable_assignment":
            self.analyze_variable_assignment(action)
        elif action_type == "shiftElement":
            self.analyze_shift_element(action)
        else:
            self.errors.append(f"Erro semântico: ação desconhecida '{action_type}'.")

    def analyze_shift_element(self, statement):
        """Analisa a ação de deslocar um elemento."""
        element_id = statement["element_id"].strip("\"")
        
        if element_id not in self.symbol_table["variables"]:
            self.errors.append(f"Erro semântico: o elemento '{element_id}' não foi declarado como variável.")
        
        x = statement.get("x", 0)
        y = statement.get("y", 0)
        
        if not isinstance(x, int) or not isinstance(y, int):
            self.errors.append(f"Erro semântico: deslocamentos 'x' e 'y' devem ser números inteiros.")

    def analyze_set_property(self, statement):
        """Analisa setProperty."""
        element_id = statement["element_id"].strip("\"")
        if element_id not in self.symbol_table["elements"]:
            self.errors.append(f"Erro semântico: o elemento '{element_id}' não foi declarado.")
        else:
            expression = statement.get("expression", [])
            self.symbol_table["elements"][element_id]["last_set_property"] = expression

    def report_errors(self):
        """Exibe erros encontrados."""
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