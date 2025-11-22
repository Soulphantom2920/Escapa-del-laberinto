import tkinter as tk
import random 
from mapa import Mapa  
from entidades import Jugador, Enemigo

# Constantes:
TITULO_JUEGO = "Escapa del Laberinto"
FPS = 30
tiempo_ciclo = 1000 // FPS 
tamano_celda = 30 

# Dificultades
enemigos_facil = 3
enemigos_medio = 6
enemigos_dificil = 10
enemigos_base = enemigos_facil #temporal

# Colores 
color_fondo     = "#222222"
color_muro      = "#555555"   
color_camino    = "#BBBBBB" 
color_tunel     = "#8B4513"  
color_liana     = "#006400"  
color_salida    = "#00FF00"
color_hud       = "#1A1A1A"
color_jugador   = "#00AAFF" 
color_enemigo   = "#FF0000"
color_jugador_corriendo = "#0055FF" 
color_jugador_cansado   = "#550000" 

class JuegoTK:
    """
    Clase principal que maneja la GUI de Tkinter y la lógica central del juego.
    """
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title(TITULO_JUEGO)

        try:
            self.ventana.state("zoomed")
        except:
            self.ventana.attributes("-fullscreen", True)

        self.ventana.update_idletasks()
        ancho_pantalla = self.ventana.winfo_screenwidth()
        alto_pantalla = self.ventana.winfo_screenheight()
        
        altura_hud = 60 
        cols = ancho_pantalla // tamano_celda
        fils = (alto_pantalla - altura_hud) // tamano_celda 

        # crear el mapa
        self.mapa = Mapa(fils, cols) 
        
        ancho_ventana = self.mapa.columnas * tamano_celda
        alto_ventana = self.mapa.filas * tamano_celda + altura_hud
        
        self.ventana.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")
        self.ventana.resizable(False, False)
        self.ventana.configure(bg=color_hud)

        self.jugador = Jugador(self.mapa.inicio_i, self.mapa.inicio_j)
        
        # comenzar lista de enemigos
        self.lista_enemigos = []
        self.arrancar_enemigos(enemigos_base)

        # GUI
        self.frame_info = tk.Frame(self.ventana, bg=color_hud, height=altura_hud)
        self.frame_info.pack(side="top", fill="x")
        self.frame_info.pack_propagate(False) 
        
        self.lbl_energia = tk.Label(
            self.frame_info, 
            text="Energía: 100%", 
            fg="white",
            bg=color_hud,
            font=("Consolas", 14, "bold"))
        
        self.lbl_energia.pack(side="left", padx=30, pady=15)

        self.frame_mapa = tk.Frame(self.ventana, bg="black")
        self.frame_mapa.pack(side="bottom", fill="both", expand=True)

        self.celdas_frames = []
        self.inicializar_mapa_visual()
        self.actualizar_graficos_jugador()

        # Controles
        self.teclas_presionadas = {} 
        self.ventana.bind("<KeyPress>", self.al_presionar_tecla)
        self.ventana.bind("<KeyRelease>", self.al_soltar_tecla)        
        self.ventana.after(tiempo_ciclo, self.ciclo_juego)

    def arrancar_enemigos(self, cantidad):
        """
        Crea la cantidad de enemigos definida por la dificultad y los ubica en el mapa.
        """
        contador = 0
        while contador < cantidad:
            i = random.randrange(1, self.mapa.filas-1, 2)
            j = random.randrange(1, self.mapa.columnas-1, 2)
            
            pos_enemigo = (i, j)
            pos_jugador = (self.jugador.i_pos, self.jugador.j_pos)
            
            if pos_enemigo != pos_jugador:
                nuevo_enemigo = Enemigo(i, j, velocidad=0.3)
                self.lista_enemigos.append(nuevo_enemigo)
                contador += 1

    def al_presionar_tecla(self, event):
        tecla = event.keysym.lower()
        self.teclas_presionadas[tecla] = True
        
    def al_soltar_tecla(self, event):
        tecla = event.keysym.lower()
        self.teclas_presionadas[tecla] = False

    def ciclo_juego(self):
        """Loop del juego"""
        shift_presionado = self.teclas_presionadas.get('shift_l') or self.teclas_presionadas.get('shift_r')
        self.jugador.actualizar_correr(shift_presionado)

        self.procesar_movimiento()
        
        if not self.jugador.esta_corriendo or self.jugador.en_fatiga:
             self.jugador.manejar_energia(False)

        self.mover_enemigos()

        estado_txt = " ⚠️ CANSADO" if self.jugador.en_fatiga else ""
        color_texto = "white"
        if self.jugador.en_fatiga: color_texto = "#FF5555" 
        elif self.jugador.esta_corriendo: color_texto = "#55AAFF" 
            
        self.lbl_energia.config(text=f"Energía: {int(self.jugador.energia_actual)}%{estado_txt}", fg=color_texto)
        self.actualizar_graficos_jugador()
        self.ventana.after(tiempo_ciclo, self.ciclo_juego)

    def mover_enemigos(self):
        """
        Mueve a cada enemigo y actualiza el gráfico.
        """
        for enemigo in self.lista_enemigos:
            old_i, old_j = enemigo.fila_actual, enemigo.columna_actual
            self.restaurar_color_celda(old_i, old_j)
            enemigo.mover_hacia_jugador(self.jugador.i_pos, self.jugador.j_pos, self.mapa)
            new_i, new_j = enemigo.fila_actual, enemigo.columna_actual
            self.celdas_frames[new_i][new_j].configure(bg=color_enemigo)

    def procesar_movimiento(self):
        cambio_i, cambio_j = 0,0
        
        if self.teclas_presionadas.get('w'): cambio_i   = -1
        elif self.teclas_presionadas.get('s'): cambio_i =  1
        elif self.teclas_presionadas.get('a'): cambio_j = -1
        elif self.teclas_presionadas.get('d'): cambio_j =  1
        
        if cambio_i != 0 or cambio_j != 0:
            old_i, old_j = self.jugador.i_pos, self.jugador.j_pos
            se_movio = self.jugador.intentar_mover(cambio_i, cambio_j, self.mapa)
            
            if se_movio:
                self.restaurar_color_celda(old_i, old_j)
                self.jugador.manejar_energia(True)
            
            elif self.jugador.esta_corriendo:
                self.jugador.manejar_energia(True) 

            self.actualizar_graficos_jugador()

    def restaurar_color_celda(self, i, j):
        """Pinta la celda de su color original segun su tipo."""
        casilla = self.mapa.matriz[i][j]
        color = color_camino

        if casilla.tipo == "muro": color = color_muro
        elif casilla.es_salida: color = color_salida
        elif casilla.tipo == "liana": color = color_liana 
        elif casilla.tipo == "tunel": color = color_tunel  
        
        if (i, j) != (self.jugador.i_pos, self.jugador.j_pos):
             self.celdas_frames[i][j].configure(bg=color)

    def inicializar_mapa_visual(self):
        self.frame_mapa.grid_rowconfigure(0, weight=1)
        self.frame_mapa.grid_columnconfigure(0, weight=1)
        
        self.contenedor_grilla = tk.Frame(self.frame_mapa, bg=color_fondo)
        self.contenedor_grilla.pack(expand=True)

        for i in range(self.mapa.filas):
            fila_frames = []
            for j in range(self.mapa.columnas):
                casilla = self.mapa.matriz[i][j]
                #determinar el color inicial                
                color = color_camino
                if casilla.tipo == "muro": color = color_muro
                elif casilla.es_salida: color = color_salida
                elif casilla.tipo == "liana": color = color_liana
                elif casilla.tipo == "tunel": color = color_tunel
                
                frame = tk.Frame(
                    self.contenedor_grilla, 
                    width=tamano_celda, 
                    height=tamano_celda, 
                    bg=color, 
                    borderwidth=1, 
                    relief="solid")
                
                frame.grid(row=i, column=j)
                frame.grid_propagate(False)
                fila_frames.append(frame)
            self.celdas_frames.append(fila_frames)

    def actualizar_graficos_jugador(self):
        i, j = self.jugador.i_pos, self.jugador.j_pos
        frame = self.celdas_frames[i][j]
        color = color_jugador
        
        if self.jugador.en_fatiga: color = color_jugador_cansado 
        elif self.jugador.esta_corriendo: color = color_jugador_corriendo
        frame.configure(bg=color)

    def iniciar(self):
        self.ventana.mainloop()