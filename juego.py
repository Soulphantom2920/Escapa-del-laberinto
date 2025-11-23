import tkinter as tk
import random 
import sys
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
color_fondo    = "#222222"
color_muro     = "#555555"   
color_camino   = "#BBBBBB" 
color_tunel    = "#8B4513"  
color_liana    = "#006400"  
color_salida   = "#00FF00"
color_hud      = "#1A1A1A"
color_jugador  = "#00AAFF" 
color_enemigo  = "#FF0000"
color_jugador_corriendo = "#0055FF" 
color_jugador_cansado   = "#550000" 
color_victoria = "#2E8B57" 
color_derrota  = "#8B0000" 

class JuegoTK:
    """
    Clase principal que maneja la GUI de Tkinter y la lógica central del juego.
    """
    def __init__(self, callback_volver=None):
        self.callback_volver = callback_volver
        
        self.ventana = tk.Toplevel() 
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
        
        self.juego_terminado = False
        self.en_pausa = False 
        self.frame_overlay = None

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
        
        tk.Label(self.frame_info, text="[ESC] PAUSA", fg="#777777", bg=color_hud).pack(side="right", padx=20)

        self.frame_mapa = tk.Frame(self.ventana, bg="black")
        self.frame_mapa.pack(side="bottom", fill="both", expand=True)

        self.celdas_frames = []
        self.inicializar_mapa_visual()
        self.actualizar_graficos_jugador()

        # Controles
        self.teclas_presionadas = {} 
        self.ventana.bind("<KeyPress>", self.al_presionar_tecla)
        self.ventana.bind("<KeyRelease>", self.al_soltar_tecla)
        self.ventana.bind("<Escape>", self.alternar_pausa)        
        
        self.ventana.protocol("WM_DELETE_WINDOW", self.salir_al_menu)

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

    def alternar_pausa(self, event=None):
        if self.juego_terminado: return 
        
        self.en_pausa = not self.en_pausa
        
        if self.en_pausa:
            self.mostrar_overlay_menu(
                titulo="JUEGO EN PAUSA",
                bg_color="#333333",
                opciones=[("REANUDAR", self.alternar_pausa),
                          ("VOLVER AL MENÚ", self.salir_al_menu),
                          ("SALIR DEL JUEGO", self.salir_del_todo)])
        else:
            if self.frame_overlay is not None:
                self.frame_overlay.destroy()
                self.frame_overlay = None

    def ciclo_juego(self):
        """Loop del juego"""
        
        # si el juego terminó, se detiene el ciclo
        if self.juego_terminado:
            return

        if self.en_pausa:
            self.ventana.after(tiempo_ciclo, self.ciclo_juego)
            return

        shift_presionado = self.teclas_presionadas.get('shift_l') or self.teclas_presionadas.get('shift_r')
        self.jugador.actualizar_correr(shift_presionado)

        self.procesar_movimiento()
        
        # ver las condiciones al mover al jugador
        if self.verificar_victoria():
            self.terminar_juego(gano=True)
            return
        
        if self.verificar_colisiones():
            self.terminar_juego(gano=False)
            return

        if not self.jugador.esta_corriendo or self.jugador.en_fatiga:
             self.jugador.manejar_energia(False)

        self.mover_enemigos()

        # ver las condiciones al mover al enemigos
        if self.verificar_colisiones():
            self.terminar_juego(gano=False)
            return

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
    
    def verificar_victoria(self):
        """
        Retorna True si el jugador toca la salida.
        """
        i, j = self.jugador.i_pos, self.jugador.j_pos
        return self.mapa.matriz[i][j].es_salida

    def verificar_colisiones(self):
        """
        Retorna True si un enemigo toca al jugador.
        """
        p_i, p_j = self.jugador.i_pos, self.jugador.j_pos
        for enemigo in self.lista_enemigos:
            if (enemigo.fila_actual == p_i) and (enemigo.columna_actual == p_j):
                return True
        return False

    def terminar_juego(self, gano):
        """
        Muestra el mensaje y detiene el loop.
        """
        self.juego_terminado = True
        
        if gano:
            t = "¡VICTORIA!"
            sub = "Has escapado del laberinto"
            c = color_victoria
        else:
            t = "GAME OVER"
            sub = "Te han atrapado..."
            c = color_derrota

        self.mostrar_overlay_menu(
            titulo=t,
            mensaje_extra=sub,
            bg_color=c,
            opciones=[("JUGAR DE NUEVO", self.reiniciar_partida),
                      ("VOLVER AL MENÚ", self.salir_al_menu)])

    def mostrar_overlay_menu(self, titulo, bg_color, opciones, mensaje_extra=""):
        """
        Crea un cuadro flotante con el contenido centrado.
        """
        
        if self.frame_overlay is not None:
            self.frame_overlay.destroy()
            self.frame_overlay = None

        ancho_msg, alto_msg = 500, 550 
        screen_w = self.ventana.winfo_width()
        screen_h = self.ventana.winfo_height()
        x = (screen_w // 2) - (ancho_msg // 2)
        y = (screen_h // 2) - (alto_msg // 2)

        self.frame_overlay = tk.Frame(self.ventana, bg=bg_color, bd=4, relief="ridge")
        self.frame_overlay.place(x=x, y=y, width=ancho_msg, height=alto_msg)
        
        # Contenedor interno
        contenedor_central = tk.Frame(self.frame_overlay, bg=bg_color)
        contenedor_central.place(relx=0.5, rely=0.5, anchor="center", width=ancho_msg-40)

        tk.Label(contenedor_central, text=titulo, bg=bg_color, fg="white", font=("Arial", 28, "bold")).pack(pady=(0, 20))
        
        if mensaje_extra:
            tk.Label(contenedor_central, text=mensaje_extra, bg=bg_color, fg="#DDDDDD", font=("Arial", 14)).pack(pady=(0, 30))

        for texto, comando in opciones:
            btn = tk.Button(contenedor_central, text=texto, 
                            font=("Arial", 12, "bold"),
                            bg="#444444", fg="white", 
                            activebackground="#666666",
                            relief="raised", 
                            cursor="hand2", 
                            command=comando)
            btn.pack(pady=10, fill="x", padx=50)

    def reiniciar_partida(self):
        self.ventana.destroy()
        JuegoTK(callback_volver=self.callback_volver)

    def salir_al_menu(self):
        self.ventana.destroy()
        if self.callback_volver:
            self.callback_volver()
            
    def salir_del_todo(self):
        self.ventana.destroy()
        sys.exit()

    def restaurar_color_celda(self, i, j):
        """
        Pinta la celda de su color original segun su tipo.
        """
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
                
                frame = tk.Frame(self.contenedor_grilla, width=tamano_celda, height=tamano_celda, bg=color, borderwidth=1, relief="solid")
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
        pass