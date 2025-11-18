import tkinter as tk
from mapa import Mapa  

# Constantes 

TITULO_JUEGO = "Escapa del Laberinto"

# Tamaño del mapa
filas_mapa = 20
columnas_mapa = 30
tamano_celda = 30 

# Tamaño de la ventana
ancho_ventana = columnas_mapa * tamano_celda
alto_ventana = filas_mapa * tamano_celda

# Colores 
color_fondo = "#222222"
color_muro = "#555555"   
color_camino = "#BBBBBB" 

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
        self.frame_mapa = tk.Frame(self.ventana)
        self.frame_mapa.pack() 

        # Logica del mapa
        self.mapa = Mapa(filas_mapa, columnas_mapa)

        self.dibujar_mapa()

    def dibujar_mapa(self):
        """
        Recorre la matriz del mapa y dibuja cada celda en el frame_mapa.
        """
        for i in range(self.mapa.filas):
            for j in range(self.mapa.columnas):

                casilla = self.mapa.matriz[i][j]
                color_celda = color_camino 
                
                if casilla.tipo == "muro":
                    color_celda = color_muro

                celda_frame = tk.Frame(
                    self.frame_mapa,
                    width=tamano_celda,
                    height=tamano_celda,
                    bg=color_celda,
                    borderwidth=1,
                    relief="solid")

                celda_frame.grid(row=i, column=j)
                celda_frame.grid_propagate(False)

    def iniciar(self):
        """
        Inicia el bucle principal de Tkinter.
        """
        self.ventana.mainloop()