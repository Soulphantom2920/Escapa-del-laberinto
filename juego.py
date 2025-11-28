import tkinter as tk
import random 
import sys
import time
import pygame #para el audio
import os
from mapa import Mapa  
from entidades import Jugador, Enemigo
from puntuaciones import guardar_puntaje 

# Constantes:
TITULO_JUEGO = "Escapa del Laberinto"
FPS = 30
tiempo_ciclo = 1000 // FPS 
tamano_celda = 30 

    #Dificultades: 
#cantidad de enemigos
enemigos_facil   = 2
enemigos_medio   = 4
enemigos_dificil = 6 
#multiplicadores de puntaje 
multiplicador_facil   = 1.0
multiplicador_medio   = 1.5
multiplicador_dificil = 2.0

# Configuración del modo cazador
tiempo_cazador   = 60 #segundos
puntos_atrapar   = 150
puntos_escaparon = 75

# Puntos de Escapa
base_escapa = 500
tiempo_escapa = 120 
bono_x_segundo = 10
bono_matar_cazador = 100

# Colores 
color_fondo    = "#392946"
color_muro     = "#555555"   
color_camino   = "#BBBBBB" 
color_tunel    = "#884e48"  
color_liana    = "#2c645e"  
color_salida   = "#fbf236"

color_hud      = "#181425"
color_jugador  = "#639bff" 
color_enemigo  = "#ac3232"

color_jugador_corriendo = "#A600FF" 
color_jugador_cansado   = "#002A7F" 
color_victoria = "#37946e" 
color_derrota  = "#9b0e3e" 
color_trampa   = "#cd6612" 

class JuegoTK:
    """
    Clase principal que maneja la GUI de Tkinter y la lógica central del juego.
    """
    def __init__(self, modo="escapa", dificultad="facil", nombre_jugador="Jugador", callback_volver=None):
        self.modo = modo
        self.dificultad = dificultad
        self.nombre_jugador = nombre_jugador
        self.callback_volver = callback_volver

        #iniciar los mp3
        pygame.mixer.init()
        try:
            # música de fondo
            pygame.mixer.music.load(os.path.join("recursos", "musica_fondo.mp3"))
            pygame.mixer.music.play(-1) # Loop infinito
            pygame.mixer.music.set_volume(0.4) 

            # efectos de sonido
            self.s_trampa = pygame.mixer.Sound(os.path.join("recursos", "poner_trampa.mp3"))
            self.s_captura = pygame.mixer.Sound(os.path.join("recursos", "captura.mp3"))
            self.s_escape = pygame.mixer.Sound(os.path.join("recursos", "escape_enemigo.mp3"))
            self.s_victoria = pygame.mixer.Sound(os.path.join("recursos", "victoria.mp3"))
            self.s_gameover = pygame.mixer.Sound(os.path.join("recursos", "game_over.mp3"))
        except Exception as e:
            print(f"Error sonidos: {e}")
            self.s_trampa = None
            self.s_captura = None
            self.s_escape = None
            self.s_victoria = None
            self.s_gameover = None

        #factores de dificultad
        self.factor_dificultad = multiplicador_facil
        if self.dificultad == "medio": self.factor_dificultad = multiplicador_medio
        elif self.dificultad == "dificil": self.factor_dificultad = multiplicador_dificil
        
        self.ventana = tk.Toplevel() 
        titulo_ventana = f"{TITULO_JUEGO} - {self.modo.upper()} ({self.dificultad.upper()})"
        self.ventana.title(titulo_ventana)

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

        # Variables propias de cada modo
        self.puntaje = 0
        self.enemigos_eliminados_trampa = 0 
        self.tiempo_inicio_juego = time.time()

        # Arreglo para que no siga el timer cuando pausamos el juego:
        self.tiempo_total_pausado = 0  # acumula cuanto tiempo se perdio en pausas
        self.momento_pausa_inicio = 0  # marca cuando se presionó ESC

        self.tiempo_limite = tiempo_cazador 

        # GUI
        self.frame_info = tk.Frame(self.ventana, bg=color_hud, height=altura_hud)
        self.frame_info.pack(side="top", fill="x")
        self.frame_info.pack_propagate(False) 
        
        # Energía
        self.lbl_energia = tk.Label(
            self.frame_info, 
            text="Energía: 100%", 
            fg="white",
            bg=color_hud,
            font=("Consolas", 14, "bold"))
        self.lbl_energia.pack(side="left", padx=(30, 20), pady=15)

        # HUD de información para los dos modos
        self.lbl_trampas = None
        self.lbl_puntaje = None
        self.lbl_tiempo = None

        if self.modo == "escapa":
            # Trampas
            self.lbl_trampas = tk.Label(self.frame_info, 
                                        text="Trampas: 3", 
                                        fg="white", 
                                        bg=color_hud, 
                                        font=("Consolas", 14, "bold"))
            self.lbl_trampas.pack(side="left", padx=20, pady=15)
            
            self.lbl_tiempo = tk.Label(self.frame_info, 
                                       text="Tiempo: 0s", 
                                       fg="white", 
                                       bg=color_hud, 
                                       font=("Consolas", 14, "bold"))
            self.lbl_tiempo.pack(side="left", padx=20, pady=15)
            
            self.lbl_puntaje = tk.Label(self.frame_info, 
                                        text="Puntaje: 0", 
                                        fg="#FFFF00", 
                                        bg=color_hud, 
                                        font=("Consolas", 14, "bold"))
            self.lbl_puntaje.pack(side="left", padx=20, pady=15)
        
        elif self.modo == "cazador":
            self.lbl_puntaje = tk.Label(self.frame_info, 
                                        text="Puntaje: 0", 
                                        fg="#FFFF00", 
                                        bg=color_hud, 
                                        font=("Consolas", 14, "bold"))
            self.lbl_puntaje.pack(side="left", padx=20, pady=15)
            
            self.lbl_tiempo = tk.Label(self.frame_info, 
                                       text=f"Tiempo: {self.tiempo_limite}", 
                                       fg="white", 
                                       bg=color_hud, 
                                       font=("Consolas", 14, "bold"))
            self.lbl_tiempo.pack(side="left", padx=20, pady=15)
        
        tk.Label(self.frame_info, 
                 text=f"JUGADOR: {self.nombre_jugador}", 
                 fg="#777777", 
                 bg=color_hud, 
                 font=("Arial", 10)).pack(side="right", padx=20)
        
        tk.Label(self.frame_info, 
                 text="[ESC] PAUSA", 
                 fg="#777777", 
                 bg=color_hud).pack(side="right", padx=20)

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
        self.ventana.bind("<space>", self.al_presionar_espacio)    
        
        self.ventana.protocol("WM_DELETE_WINDOW", self.salir_al_menu)

        # lista de enemigos 
        self.lista_enemigos = []
        cant_enemigos = enemigos_facil
        if self.dificultad == "medio": cant_enemigos = enemigos_medio
        elif self.dificultad == "dificil": cant_enemigos = enemigos_dificil

        if self.modo == "cazador":
            cant_enemigos += 1 
        self.arrancar_enemigos(cant_enemigos)

        self.ventana.after(tiempo_ciclo, self.ciclo_juego)

    def arrancar_enemigos(self, cantidad):
        #configuración de la velocidad
        vel = 0.27  # Base por defecto
        
        if self.modo == "escapa":
            vel = 0.27
            if self.dificultad == "medio": vel = 0.24
            elif self.dificultad == "dificil": vel = 0.21
            
        elif self.modo == "cazador":
            vel = 0.21
            if self.dificultad == "medio": vel = 0.19
            elif self.dificultad == "dificil": vel = 0.16

        contador = 0
        intentos = 0
        while contador < cantidad and intentos < 1000:
            i = random.randrange(1, self.mapa.filas-1, 2)
            j = random.randrange(1, self.mapa.columnas-1, 2)
            intentos += 1
            
            #validar una distancia segura respecto al jugador
            distancia_jugador = abs(i-self.jugador.i_pos) + abs(j-self.jugador.j_pos)
            #si está a menos de 10 casillas, se busca otra posición
            if distancia_jugador < 10:
                continue

            # validacion en el modo cazador
            if self.modo == "cazador":
                dist_salida = abs(i-self.mapa.salida_i) + abs(j-self.mapa.salida_j)
                if dist_salida < 15:
                    continue

            nuevo_enemigo = Enemigo(i, j, velocidad=vel)
            self.lista_enemigos.append(nuevo_enemigo)
            contador += 1
    
    def respawn_enemigo(self):
        """
        Genera un nuevo enemigo.
        """
        if self.juego_terminado: return
        #velocidades separadas
        vel = 0.27

        if self.modo == "escapa":
            vel = 0.27
            if self.dificultad == "medio": vel = 0.24
            elif self.dificultad == "dificil": vel = 0.21
            
        elif self.modo == "cazador":
            vel = 0.21
            if self.dificultad == "medio": vel = 0.19
            elif self.dificultad == "dificil": vel = 0.16

        creado = False
        intentos = 0
        while not creado and intentos < 100:
            i = random.randrange(1, self.mapa.filas-1)
            j = random.randrange(1, self.mapa.columnas-1)
            intentos += 1
            
            # Solo en camino
            if self.mapa.matriz[i][j].es_accesible_enemigo:
                #distancia para el respawn
                distancia_jugador = abs(i - self.jugador.i_pos) + abs(j - self.jugador.j_pos)
                if distancia_jugador < 10:
                    continue
                    
                if self.modo == "cazador":
                    dist_salida = abs(i - self.mapa.salida_i) + abs(j - self.mapa.salida_j)
                    if dist_salida < 15:
                        continue

                nuevo = Enemigo(i, j, velocidad=vel)
                self.lista_enemigos.append(nuevo)
                creado = True

    def al_presionar_tecla(self, event):
        tecla = event.keysym.lower()
        self.teclas_presionadas[tecla] = True
        
    def al_soltar_tecla(self, event):
        tecla = event.keysym.lower()
        self.teclas_presionadas[tecla] = False

    def al_presionar_espacio(self, event):
        """
        Pone una trampa.
        """
        if self.juego_terminado or self.en_pausa: return
        if self.modo != "escapa": return #desactivado en modo cazador

        if self.jugador.intentar_colocar_trampa(self.mapa):
            i, j = self.jugador.i_pos, self.jugador.j_pos
            self.celdas_frames[i][j].configure(bg=color_trampa)
            self.actualizar_graficos_jugador()
            if self.s_trampa: self.s_trampa.play() #sonido d la trampa

    def alternar_pausa(self, event=None):
        if self.juego_terminado: return 
        self.en_pausa = not self.en_pausa        
        if self.en_pausa:
            self.momento_pausa_inicio = time.time() #guarda la hora de la pausa
            #pausar la música
            pygame.mixer.music.pause()
            self.mostrar_overlay_menu(
                titulo="JUEGO EN PAUSA",
                bg_color="#333333",
                opciones=[("REANUDAR", self.alternar_pausa), 
                          ("VOLVER AL MENÚ", self.salir_al_menu),
                          ("SALIR DEL JUEGO", self.salir_del_todo)])
        else:
            tiempo_en_pausa = time.time() - self.momento_pausa_inicio
            self.tiempo_total_pausado += tiempo_en_pausa
            #reanudar la música
            pygame.mixer.music.unpause()
            if self.frame_overlay is not None:
                self.frame_overlay.destroy()
                self.frame_overlay = None

    def ciclo_juego(self):
        """Loop del juego"""
        if self.juego_terminado: return

        if self.en_pausa:
            self.ventana.after(tiempo_ciclo, self.ciclo_juego)
            return

        tiempo_actual = time.time()
        tiempo_pasado = tiempo_actual - self.tiempo_inicio_juego - self.tiempo_total_pausado
        
        # Actualizar la lógica dependiendo del modo
        if self.modo == "cazador":
            restante = int(self.tiempo_limite - tiempo_pasado)
            if restante <= 0:
                restante = 0
                self.lbl_tiempo.config(text=f"Tiempo: {restante}")
                self.terminar_juego(gano=True) 
                return
            self.lbl_tiempo.config(text=f"Tiempo: {restante}")
        
        elif self.modo == "escapa":
            segundos_sobra = max(0, int(tiempo_escapa-tiempo_pasado))
            bono_tiempo = segundos_sobra * bono_x_segundo
            bono_caza = self.enemigos_eliminados_trampa * bono_matar_cazador
            puntaje_actual = int((base_escapa+bono_tiempo+bono_caza) * self.factor_dificultad)
            
            self.lbl_tiempo.config(text=f"Tiempo: {int(tiempo_pasado)}s")
            self.lbl_puntaje.config(text=f"Puntaje: {puntaje_actual}")

        shift_presionado = self.teclas_presionadas.get('shift_l') or self.teclas_presionadas.get('shift_r')
        self.jugador.actualizar_correr(shift_presionado)
        self.procesar_movimiento()
        
        # verificar victoria/colisión
        if self.modo == "escapa":
            if self.verificar_victoria(): #escapó
                self.terminar_juego(gano=True)
                return
            if self.verificar_colisiones(): #lo tocaron
                self.terminar_juego(gano=False)
                return
        elif self.modo == "cazador":
            self.verificar_colisiones() 

        if not self.jugador.esta_corriendo or self.jugador.en_fatiga:
             self.jugador.manejar_energia(False)

        # mover a los enemigos
        self.mover_enemigos()

        if self.modo == "escapa":
            if self.verificar_colisiones():
                self.terminar_juego(gano=False)
                return
        elif self.modo == "cazador":
            self.verificar_colisiones()

        # actualizar toda la HUD
        estado_txt = " ⚠️ CANSADO" if self.jugador.en_fatiga else ""
        color_texto = "white"
        if self.jugador.en_fatiga: color_texto = "#FF5555" 
        elif self.jugador.esta_corriendo: color_texto = "#55AAFF" 
        self.lbl_energia.config(text=f"Energía: {int(self.jugador.energia_actual)}%{estado_txt}", fg=color_texto)

        if self.modo == "escapa":
            trampas_restantes = self.jugador.max_trampas_activas - len(self.jugador.trampas_colocadas)
            en_cooldown = (tiempo_actual - self.jugador.contador_cooldown) < self.jugador.cooldown_trampa
            if en_cooldown and trampas_restantes < 3:
                self.lbl_trampas.config(text="Recargando...", fg="yellow")
            else:
                self.lbl_trampas.config(text=f"Trampas: {trampas_restantes}", fg="white")

        self.actualizar_graficos_jugador()
        self.ventana.after(tiempo_ciclo, self.ciclo_juego)

    def mover_enemigos(self):
        """
        Mueve enemigos segun el modo.
        """
        enemigos_a_borrar = [] 

        p_i, p_j = self.jugador.i_pos, self.jugador.j_pos
        casilla_jugador = self.mapa.matriz[p_i][p_j]
        estado_original_acceso = casilla_jugador.es_accesible_enemigo        
        
        # en el modo cazador, ahora el jugador es un muro temporalmente, 
        # así se puede evitar que nos pasen por encima los enemigos
        if self.modo == "cazador":
            casilla_jugador.es_accesible_enemigo = False

        for enemigo in self.lista_enemigos:
            old_i, old_j = enemigo.fila_actual, enemigo.columna_actual
            self.restaurar_color_celda(old_i, old_j)
            
            if self.modo == "escapa":
                #persigue al jugador
                enemigo.mover_hacia_jugador(self.jugador.i_pos, self.jugador.j_pos, self.mapa)
            
            elif self.modo == "cazador":
                # Lógica de evasión:
                # calcula la distancia al jugador
                dist_jugador = abs(enemigo.fila_actual-self.jugador.i_pos) + abs(enemigo.columna_actual-self.jugador.j_pos)
                
                # el destino es la salida
                i_objetivo, j_objetivo = self.mapa.salida_i, self.mapa.salida_j

                # si el jugador está muy cerca el enemigo huye lejos de nosotros
                if dist_jugador < 3: #distancia a la que nos notan
                    #4 esquinas seguras:
                    esquinas = [(1, 1), (1, self.mapa.columnas-2),(self.mapa.filas-2, 1),(self.mapa.filas-2, self.mapa.columnas-2)]
                    
                    # se busca cual esquina está más lejos del jugador para correr hacia ella
                    mejor_esquina = esquinas[0]
                    max_dist = -1
                    
                    for (esq_i, esq_j) in esquinas:
                        d = abs(esq_i - self.jugador.i_pos) + abs(esq_j - self.jugador.j_pos)
                        if d > max_dist:
                            max_dist = d
                            mejor_esquina = (esq_i, esq_j)
                    i_objetivo, j_objetivo = mejor_esquina
                #se mueve al objetivo sSalida o esquina lejana al jugador)
                enemigo.mover_hacia_jugador(i_objetivo, j_objetivo, self.mapa)
            
            new_i, new_j = enemigo.fila_actual, enemigo.columna_actual
            
            casilla = self.mapa.matriz[new_i][new_j]            
            # MODO ESCAPA: Trampas
            if self.modo == "escapa" and casilla.es_trampa:
                casilla.es_trampa = False
                self.jugador.remover_trampa_de_lista(new_i, new_j)
                self.restaurar_color_celda(new_i, new_j)
                enemigos_a_borrar.append(enemigo)
                self.enemigos_eliminados_trampa += 1 #el bono
                self.ventana.after(10000, self.respawn_enemigo)
                if self.s_captura: self.s_captura.play() #sonido de captura para la trampa
            
            # MODO CAZADOR: Enemigo llega a la salida
            elif self.modo == "cazador" and casilla.es_salida:
                #el enemigo se esccapó
                self.puntaje -= puntos_escaparon
                if self.puntaje < 0: self.puntaje = 0
                
                #mostrar puntos en el HUD
                puntos_reales = int(self.puntaje * self.factor_dificultad)
                self.lbl_puntaje.config(text=f"Puntaje: {puntos_reales}")
                
                if self.s_escape: self.s_escape.play() #sonido de escape
                enemigos_a_borrar.append(enemigo)
                self.respawn_enemigo()
            else:
                self.celdas_frames[new_i][new_j].configure(bg=color_enemigo)

        if self.modo == "cazador":
            casilla_jugador.es_accesible_enemigo = estado_original_acceso

        for e in enemigos_a_borrar:
            if e in self.lista_enemigos:
                self.lista_enemigos.remove(e)

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
        """Retorna True si el jugador toca la salida (Modo Escapa)."""
        i, j = self.jugador.i_pos, self.jugador.j_pos
        return self.mapa.matriz[i][j].es_salida

    def verificar_colisiones(self):
        """
        Maneja colisiones entre el jugador y el enemigo según el modo.
        #S: True si debe terminar el juego.
        """
        p_i, p_j = self.jugador.i_pos, self.jugador.j_pos
        
        enemigos_atrapados = []

        hit = False
        for enemigo in self.lista_enemigos:
            if (enemigo.fila_actual == p_i) and (enemigo.columna_actual == p_j):
                
                if self.modo == "escapa":
                    return True #Game Over
                
                elif self.modo == "cazador":
                    #fue atrapado
                    enemigos_atrapados.append(enemigo)
                    hit = True
        
        #Procesar los atrapados en el modo cazador
        if self.modo == "cazador" and hit:
            for e in enemigos_atrapados:
                if e in self.lista_enemigos:
                    self.lista_enemigos.remove(e)
                    self.puntaje += puntos_atrapar
                    
                    puntos_reales = int(self.puntaje * self.factor_dificultad)
                    self.lbl_puntaje.config(text=f"Puntaje: {puntos_reales}")
                    
                    if self.s_captura: self.s_captura.play() # SONIDO CAPTURA
                    self.respawn_enemigo()
            return False

        return False

    def terminar_juego(self, gano):
        """
        Muestra el mensaje y detiene el loop.
        """
        self.juego_terminado = True
        
        #detener la música de fondo y poner el sonido final
        pygame.mixer.music.stop()
        if gano:
            if self.s_victoria: self.s_victoria.play()
        else:
            if self.s_gameover: self.s_gameover.play()

        titulo = ""
        mensaje = ""
        color_bg = ""
        
        puntaje_final = 0

        if self.modo == "escapa":
            if gano:
                titulo = "¡VICTORIA!"
                tiempo_tardado = time.time() - self.tiempo_inicio_juego
                bono_tiempo = 0
                if tiempo_tardado < tiempo_escapa:
                    segundos_sobra = int(tiempo_escapa - tiempo_tardado)
                    bono_tiempo = segundos_sobra * bono_x_segundo

                bono_caza = self.enemigos_eliminados_trampa * bono_matar_cazador
                puntaje_bruto = base_escapa + bono_tiempo + bono_caza
                puntaje_final = int(puntaje_bruto * self.factor_dificultad)
                
                mensaje = f"Puntaje Total: {puntaje_final}\n(Tiempo: {int(tiempo_tardado)}s)"
                color_bg = color_victoria
                guardar_puntaje("escapa", self.nombre_jugador, puntaje_final, self.dificultad) 
            else:
                titulo = "GAME OVER"
                mensaje = "Te han atrapado..."
                color_bg = color_derrota
        
        elif self.modo == "cazador":
            titulo = "TIEMPO AGOTADO"
            puntaje_final = int(self.puntaje * self.factor_dificultad)
            mensaje = f"Puntaje Final: {puntaje_final}"
            color_bg = "#C2773D"
            guardar_puntaje("cazador", self.nombre_jugador, puntaje_final, self.dificultad)

        self.mostrar_overlay_menu(
            titulo=titulo,
            mensaje_extra=mensaje,
            bg_color=color_bg,
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
        
        contenedor_central = tk.Frame(self.frame_overlay, bg=bg_color)
        contenedor_central.place(relx=0.5, rely=0.5, anchor="center", width=ancho_msg-40)

        tk.Label(contenedor_central, text=titulo, bg=bg_color, fg="white", font=("Arial", 28, "bold")).pack(pady=(0, 20))
        
        if mensaje_extra:
            tk.Label(contenedor_central, text=mensaje_extra, bg=bg_color, fg="#DDDDDD", font=("Arial", 18, "bold")).pack(pady=(0, 30))

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
        JuegoTK(modo=self.modo, 
                dificultad=self.dificultad, 
                nombre_jugador=self.nombre_jugador, 
                callback_volver=self.callback_volver)

    def salir_al_menu(self):
        #detener audio si se sale al menú
        pygame.mixer.music.stop()
        self.ventana.destroy()
        if self.callback_volver:
            self.callback_volver()
            
    def salir_del_todo(self):
        pygame.mixer.quit()
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
        elif casilla.es_trampa: color = color_trampa 
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