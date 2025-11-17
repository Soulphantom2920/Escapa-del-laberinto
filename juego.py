import tkinter as tk

# Constantes:


TITULO_JUEGO = "Escapa del Laberinto"

# Dimensiones: 
# (Por ajustar)
ancho_ventana = 800
alto_ventana = 600

# Colores 
color_fondo = "#222222" 

class JuegoTK:
    """
    Clase principal que maneja la GUI de Tkinter y la lógica central del juego.
    """
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title(TITULO_JUEGO)

        ancho_pantalla = self.ventana.winfo_screenwidth()
        alto_pantalla = self.ventana.winfo_screenheight()
        pos_x = (ancho_pantalla//2) - (ancho_ventana//2)
        pos_y = (alto_pantalla//2) - (alto_ventana//2)
        self.ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}")

        self.ventana.resizable(False, False)
        self.ventana.configure(bg=color_fondo)

        # Aquí irá el canvas para el mapa (a desarrollar después)

        # Aquí va a ir la GUI de energía, puntos, etc.

    def iniciar(self):
        """
        Inicia el bucle principal de Tkinter.
        """
        self.ventana.mainloop()