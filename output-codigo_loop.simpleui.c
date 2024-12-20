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