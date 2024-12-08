#include <gtk/gtk.h>
#include <stdio.h>
#include <string.h>

// Widgets globais
GtkWidget *widget_nome;
GtkWidget *widget_email;
GtkWidget *widget_button_3;
GtkWidget *widget_resultado;

static void on_click_button_3(GtkWidget *widget, gpointer data) {
    const char* nome = gtk_entry_get_text(GTK_ENTRY(widget_nome));
    const char* email = gtk_entry_get_text(GTK_ENTRY(widget_email));
    char buffer[1024];
    sprintf(buffer, "%s%s%s", "Nome: ", nome, ", E-mail ", email);
    gtk_label_set_text(GTK_LABEL(widget_resultado), buffer);
}

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