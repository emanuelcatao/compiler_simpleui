# Compiler SimpleUI

Projeto Desenvolvido por Luccas Castro e Emanuel Catão

## Overview

SimpleUI é uma linguagem de programação desenvolvida para abstrair a complexidade do GTK, permitindo a criação rápida de interfaces gráficas. O compilador, escrito em Python, transpila código SimpleUI para C + GTK, tornando o desenvolvimento de GUIs mais acessível e intuitivo.

> Veja o resultado no vídeo curto [Vídeo](https://github.com/emanuelcatao/compiler_simpleui/blob/main/20241208_130036Edit.mp4)

## Features

- Tradução de código SimpleUI para C + GTK
- Suporte a elementos básicos de interface (botões, inputs, labels)
- Gerenciamento de eventos (cliques e teclas)
- Posicionamento absoluto de elementos
- Sistema de variáveis e propriedades
- Análise léxica, sintática e semântica completa

## Requirements

- Python 3.10 ou superior
- GCC
- GTK 3.0
- pkg-config
- graphviz (opcional, para visualização da AST)

## Installation

### 1. Clone o repositório:
```sh
git clone https://github.com/yourusername/compiler_simpleui.git
cd compiler_simpleui
```

### 2. Instale as dependências do Python:
```sh
pip install graphviz
```

### 3. Instale o GTK e outras dependências:

Ubuntu/Debian:
```sh
sudo apt-get update
sudo apt-get install libgtk-3-dev
sudo apt-get install pkg-config
sudo apt-get install graphviz  # opcional
```

Fedora:
```sh
sudo dnf install gtk3-devel
sudo dnf install pkgconfig
sudo dnf install graphviz  # opcional
```

macOS:
```sh
brew install gtk+3
brew install pkg-config
brew install graphviz  # opcional
```

## Usage

1. Crie seu arquivo SimpleUI (por exemplo, `app.simpleui`)
2. Execute o compilador:
```sh
python3 main.py
```
3. Compile o código C gerado:
```sh
gcc `pkg-config --cflags gtk+-3.0` -o app output-app.simpleui.c `pkg-config --libs gtk+-3.0`
```
4. Execute o programa:
```sh
./app
```

## Exemplos Comparativos

### Exemplo 1: Formulário Simples

#### Em SimpleUI:
```
createWindow("Formulario", width=600, height=400);

addElement(type="input", id="nome", placeholder="Digite seu nome", x=50, y=50);
addElement(type="input", id="email", placeholder="Digite seu e-mail", x=50, y=100);
addElement(type="button", text="Enviar", x=50, y=150);
addElement(type="label", id="resultado", text="Aguardando submissao...", x=50, y=200);

onClick("button") {
    let nome = getProperty("nome", value);
    let email = getProperty("email", value);
    setProperty("resultado", text="Nome: " + nome + ", E-mail " + email);
}

```

#### Equivalente em C + GTK:
```c
#include <gtk/gtk.h>
#include <stdio.h>
#include <string.h>

// Widgets globais
GtkWidget *widget_nome;
GtkWidget *widget_email;
GtkWidget *widget_button_3;
GtkWidget *widget_resultado;

static void activate(GtkApplication *app, gpointer user_data) {
    GtkWidget *window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Formulario");
    gtk_window_set_default_size(GTK_WINDOW(window), 600, 400);
    GtkWidget *fixed = gtk_fixed_new();
    gtk_container_add(GTK_CONTAINER(window), fixed);
    widget_nome = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(widget_nome), "Digite seu nome");
    gtk_fixed_put(GTK_FIXED(fixed), widget_nome, 50, 50);
    widget_email = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(widget_email), "Digite seu e-mail");
    gtk_fixed_put(GTK_FIXED(fixed), widget_email, 50, 100);
    widget_button_3 = gtk_button_new_with_label("Enviar");
    gtk_fixed_put(GTK_FIXED(fixed), widget_button_3, 50, 150);
    g_signal_connect(widget_button_3, "clicked", G_CALLBACK(on_click_button_3), NULL);
    widget_resultado = gtk_label_new("Aguardando submissao...");
    gtk_fixed_put(GTK_FIXED(fixed), widget_resultado, 50, 200);
    gtk_widget_show_all(window);
}

int main(int argc, char *argv[]) {
    GtkApplication *app;
    int status;
    
    app = gtk_application_new("com.example.simpleui", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    
    return status;
}
```

### Exemplo 2: Animação Simples

#### Em SimpleUI:
```
createWindow("Loop", width=640, height=480);

let coisa = "oi";

onKeypress("A") {
    shiftElement("coisa", x=-10, y=0);
}
```

#### Equivalente em C + GTK:
```c
#include <gtk/gtk.h>
#include <stdio.h>
#include <string.h>

// Widgets globais
GtkWidget *widget_coisa;

// Variáveis globais
char* coisa = "oi";

static gboolean on_key_press(GtkWidget *widget, GdkEventKey *event, gpointer data) {
    switch(event->keyval) {
        case GDK_KEY_A:
            {
                GtkFixed *fixed = GTK_FIXED(gtk_widget_get_parent(widget_coisa));
                GtkAllocation allocation;
                gtk_widget_get_allocation(widget_coisa, &allocation);
                gtk_fixed_move(fixed, widget_coisa, allocation.x + -10, allocation.y + 0);
            }
            break;
    }
    return FALSE;
}

static void activate(GtkApplication *app, gpointer user_data) {
    GtkWidget *window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Loop");
    gtk_window_set_default_size(GTK_WINDOW(window), 640, 480);
    GtkWidget *fixed = gtk_fixed_new();
    gtk_container_add(GTK_CONTAINER(window), fixed);
    widget_coisa = gtk_label_new("oi");
    gtk_fixed_put(GTK_FIXED(fixed), widget_coisa, 50, 50);
    g_signal_connect(window, "key-press-event", G_CALLBACK(on_key_press), NULL);
    gtk_widget_show_all(window);
}

int main(int argc, char *argv[]) {
    GtkApplication *app;
    int status;
    
    app = gtk_application_new("com.example.simpleui", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    
    return status;
}
```

## Estrutura do Projeto

```
compiler_simpleui/
├── lexer/              # Análise léxica
├── parser/             # Análise sintática
├── analisador_semantico/ # Análise semântica
├── tradutor/           # Tradução para C + GTK
├── testes/             # Arquivos de teste
├── utils/              # Utilitários
└── main.py            # Ponto de entrada
```
