import tkinter as tk
from mapa import Mapa  
from entidades import Jugador

# Constantes 

TITULO_JUEGO = "Escapa del Laberinto"

# Tamaño del mapa
filas_mapa = 20
columnas_mapa = 30
tamano_celda = 30 

# Tamaño de la ventana
ancho_ventana = columnas_mapa * tamano_celda
alto_ventana = filas_mapa * tamano_celda + 50 

# Colores 
color_fondo = "#222222"
color_muro = "#555555"   
color_camino = "#BBBBBB" 
color_jugador = "#00AAFF" 
color_jugador_corriendo = "#0055FF" 

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

        self.mapa = Mapa(filas_mapa, columnas_mapa)
        self.jugador = Jugador(1, 1) #posicion inicial

        # Interfaz grafica
        self.frame_mapa = tk.Frame(self.ventana, width=ancho_ventana, height=alto_ventana-50)
        self.frame_mapa.pack() 
        
        # para la información:
        self.frame_info = tk.Frame(self.ventana, bg="#333333", height=50)
        self.frame_info.pack(fill="x")
        self.lbl_energia = tk.Label(self.frame_info, text="Energía: 100%", fg="white", bg="#333333", font=("Arial", 12))
        self.lbl_energia.pack(side="left", padx=20, pady=10)

        self.celdas_frames = []
        self.iniciar_visuales_mapa()
        
        # Dibujar al jugador 
        self.actualizar_graficos_jugador()

        # Controles para moverse:
        self.ventana.bind("<w>", lambda e: self.jugador_moverse(-1,0))
        self.ventana.bind("<a>", lambda e: self.jugador_moverse(0,-1))
        self.ventana.bind("<s>", lambda e: self.jugador_moverse(1,0))
        self.ventana.bind("<d>", lambda e: self.jugador_moverse(0,1))
        
        self.ventana.bind("<W>", lambda e: self.jugador_moverse(-1,0))
        self.ventana.bind("<A>", lambda e: self.jugador_moverse(0,-1))
        self.ventana.bind("<S>", lambda e: self.jugador_moverse(1,0))
        self.ventana.bind("<D>", lambda e: self.jugador_moverse(0,1))

        # Para correr:
        self.ventana.bind("<KeyPress-Shift_L>", self.correr)
        self.ventana.bind("<KeyRelease-Shift_L>", self.dejar_de_correr)

    def iniciar_visuales_mapa(self):
        """
        Crea la cuadrícula de frames y la dibuja.
        """
        for i in range(self.mapa.filas):
            frame_fila = []
            for j in range(self.mapa.columnas):
                casilla = self.mapa.matriz[i][j]
                color = color_muro if casilla.tipo == "muro" else color_camino
                
                frame = tk.Frame(
                    self.frame_mapa,
                    width=tamano_celda,
                    height=tamano_celda,
                    bg=color,
                    borderwidth=1, relief="solid")
                
                frame.grid(row=i, column=j)
                frame.grid_propagate(False)
                frame_fila.append(frame)
            self.celdas_frames.append(frame_fila)

    def jugador_moverse(self, cambio_fila, cambio_columna):
        """
        Lógica para mover al jugador y actualizar la interfaz.
        E: El cambio en fila y columna hacia donde se quiere mover.
        S: Solo actualiza la interfaz.
        """
        # limpiar la posición anterior
        old_i, old_j = self.jugador.i_pos, self.jugador.j_pos
        self.celdas_frames[old_i][old_j].configure(bg=color_camino)

        # moverse
        se_movio = self.jugador.intentar_mover(cambio_fila, cambio_columna, self.mapa)

        # energía
        self.jugador.gestionar_energia(se_movio)
        
        # actualizar los gráficos y la interfaz
        self.actualizar_graficos_jugador()
        self.lbl_energia.config(text=f"Energía: {int(self.jugador.energia_actual)}%")

    def correr(self, event):
        """Activa correr si hay energía."""
        if self.jugador.energia_actual > 0:
            self.jugador.esta_corriendo = True
            self.actualizar_graficos_jugador()

    def dejar_de_correr(self, event):
        """Desactiva correr."""
        self.jugador.esta_corriendo = False
        self.actualizar_graficos_jugador()

    def actualizar_graficos_jugador(self):
        """Pinta al jugador en su posición actual."""
        i, j = self.jugador.i_pos, self.jugador.j_pos
        frame_jugador = self.celdas_frames[i][j]
        
        if self.jugador.esta_corriendo:
            frame_jugador.configure(bg=color_jugador_corriendo)
        else:
            frame_jugador.configure(bg=color_jugador)

    def iniciar(self):
        self.ventana.mainloop()