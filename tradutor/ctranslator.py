import json

class GtkTranslator:
    def __init__(self, semantic_table):
        self.semantic_table = semantic_table
        self.code = []
        self.indent = 0
        self.has_input = False
        self.window_var = "window"
        self.elements = {}

    def _add_line(self, line):
        """Adiciona linha de código com indentação"""
        self.code.append('    ' * self.indent + line)

    def translate(self):
        """Traduz tabela semântica para código GTK"""
        self._add_line("#include <gtk/gtk.h>")
        self._add_line("#include <stdio.h>")
        self._add_line("#include <string.h>")
        self._add_line("")
        
        self._add_global_declarations()
        
        self._add_callbacks()
        
        self._add_activate_function()
        
        self._add_main()
        
        return "\n".join(self.code)

    def _add_global_declarations(self):
        """Adiciona declarações globais"""
        self._add_line("// Widgets globais")
        for element_id in self.semantic_table.get('elements', {}):
            self._add_line(f"GtkWidget *widget_{element_id};")
        
        variables = self.semantic_table.get('variables', {})
        for var_name, var_info in variables.items():
            var_type = 'char*' if var_info['type'] == 'string' else 'int'
            var_value = var_info['value'].strip('"') if var_info['type'] == 'string' else var_info['value']
            if var_type == 'char*':
                self._add_line(f"{var_type} {var_name} = \"{var_value}\";")
            else:
                self._add_line(f"{var_type} {var_name} = {var_value};")
        self._add_line("")

    def _add_callbacks(self):
        """Adiciona funções de callback para eventos"""
        events = self.semantic_table.get('events', {})
        
        # Callbacks para eventos de tecla
        if 'keypress' in events:
            self._add_line("static gboolean on_key_press(GtkWidget *widget, GdkEventKey *event, gpointer data) {")
            self.indent += 1
            self._add_line("switch(event->keyval) {")
            self.indent += 1
            
            for key, event_info in events['keypress'].items():
                self._add_line(f"case GDK_KEY_{key}:")
                self.indent += 1
                for action in event_info.get('actions', []):
                    self._translate_action(action)
                self._add_line("break;")
                self.indent -= 1
            
            self.indent -= 1
            self._add_line("}")
            self._add_line("return FALSE;")
            self.indent -= 1
            self._add_line("}")
            self._add_line("")

        for target, event_info in events.items():
            if target != 'keypress' and event_info['type'] == 'onClick':
                self._add_line(f"static void on_click_{target}(GtkWidget *widget, gpointer data) {{")
                self.indent += 1
                for action in event_info.get('actions', []):
                    self._translate_action(action)
                self.indent -= 1
                self._add_line("}")
                self._add_line("")

    def _add_activate_function(self):
        """Adiciona função de ativação principal do GTK"""
        self._add_line("static void activate(GtkApplication *app, gpointer user_data) {")
        self.indent += 1
        
        window = self.semantic_table.get('window', {})
        self._add_line(f"GtkWidget *window = gtk_application_window_new(app);")
        self._add_line(f"gtk_window_set_title(GTK_WINDOW(window), {window.get('title', '\"Untitled\"')});")
        self._add_line(f"gtk_window_set_default_size(GTK_WINDOW(window), {window.get('width', 640)}, {window.get('height', 480)});")
        
        self._add_line("GtkWidget *fixed = gtk_fixed_new();")
        self._add_line("gtk_container_add(GTK_CONTAINER(window), fixed);")
        
        elements = self.semantic_table.get('elements', {})
        for element_id, element_info in elements.items():
            self._translate_element(element_id, element_info, "fixed")
        
        if 'keypress' in self.semantic_table.get('events', {}):
            self._add_line("g_signal_connect(window, \"key-press-event\", G_CALLBACK(on_key_press), NULL);")
        
        self._add_line("gtk_widget_show_all(window);")
        
        self.indent -= 1
        self._add_line("}")
        self._add_line("")

    def _translate_element(self, element_id, element_info, container):
        """Traduz um elemento para widget GTK"""
        attrs = element_info['attributes']
        element_type = attrs['type'].strip('"')
        x = attrs.get('x', 0)
        y = attrs.get('y', 0)
        
        if element_type == "button":
            self._add_line(f"widget_{element_id} = gtk_button_new_with_label({attrs.get('text', '\"\"')});")
        elif element_type == "input":
            self._add_line(f"widget_{element_id} = gtk_entry_new();")
            if 'placeholder' in attrs:
                self._add_line(f"gtk_entry_set_placeholder_text(GTK_ENTRY(widget_{element_id}), {attrs['placeholder']});")
        elif element_type == "label":
            self._add_line(f"widget_{element_id} = gtk_label_new({attrs.get('text', '\"\"')});")
        
        self._add_line(f"gtk_fixed_put(GTK_FIXED({container}), widget_{element_id}, {x}, {y});")
        
        if element_type == "button":
            events = self.semantic_table.get('events', {})
            if element_id in events and events[element_id]['type'] == 'onClick':
                self._add_line(f"g_signal_connect(widget_{element_id}, \"clicked\", G_CALLBACK(on_click_{element_id}), NULL);")

    def _translate_action(self, action):
        """Traduz ações para código GTK"""
        action_type = action['type']
        
        if action_type == 'variable_assignment':
            if action['value']['type'] == 'function_call':
                func_name = action['value']['name']
                if func_name == 'getProperty':
                    element_id = action['value']['arguments'][0].strip('"')
                    self._add_line(f"const char* {action['name']} = gtk_entry_get_text(GTK_ENTRY(widget_{element_id}));")
        
        elif action_type == 'setProperty':
            element_id = action['element_id'].strip('"')
            if 'expression' in action:
                # Concatenar expressão
                expr_parts = []
                for part in action['expression']:
                    if part == "+":
                        continue
                    if part.startswith('"'):
                        expr_parts.append(part)
                    else:
                        expr_parts.append(part)
                expr = " ".join(expr_parts)
                self._add_line(f"char buffer[1024];")
                self._add_line(f"sprintf(buffer, \"%s%s%s\", {', '.join(expr_parts)});")
                self._add_line(f"gtk_label_set_text(GTK_LABEL(widget_{element_id}), buffer);")
        
        elif action_type == 'shiftElement':
            element_id = action['element_id'].strip('"')
            x_shift = action.get('x', 0)
            y_shift = action.get('y', 0)
            self._add_line(f"GtkFixed *fixed = GTK_FIXED(gtk_widget_get_parent(widget_{element_id}));")
            self._add_line(f"gint x, y;")
            self._add_line(f"gtk_fixed_get_child_position(fixed, widget_{element_id}, &x, &y);")
            self._add_line(f"gtk_fixed_move(fixed, widget_{element_id}, x + {x_shift}, y + {y_shift});")

    def _add_main(self):
        """Adiciona função main"""
        self._add_line("int main(int argc, char *argv[]) {")
        self.indent += 1
        self._add_line("GtkApplication *app;")
        self._add_line("int status;")
        self._add_line("")
        self._add_line("app = gtk_application_new(\"com.example.simpleui\", G_APPLICATION_FLAGS_NONE);")
        self._add_line("g_signal_connect(app, \"activate\", G_CALLBACK(activate), NULL);")
        self._add_line("status = g_application_run(G_APPLICATION(app), argc, argv);")
        self._add_line("g_object_unref(app);")
        self._add_line("")
        self._add_line("return status;")
        self.indent -= 1
        self._add_line("}")