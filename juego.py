import tkinter as tk
import random 
import sys
import time
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
puntos_escaparon = 50

# Puntos de Escapa
base_escapa = 500
tiempo_escapa = 120 
bono_x_segundo = 10
bono_matar_cazador = 100

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
color_trampa   = "#FF00FF" 

class JuegoTK:
    """
    Clase principal que maneja la GUI de Tkinter y la lógica central del juego.
    """
    def __init__(self, modo="escapa", dificultad="facil", nombre_jugador="Jugador", callback_volver=None):
        self.modo = modo
        self.dificultad = dificultad
        self.nombre_jugador = nombre_jugador
        self.callback_volver = callback_volver

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
        # velocidad:
        vel = 0.27 #base 
        if self.dificultad == "medio": vel = 0.25 
        elif self.dificultad == "dificil": vel = 0.22

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
        
        vel = 0.27
        if self.dificultad == "medio": vel = 0.25
        elif self.dificultad == "dificil": vel = 0.22

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
        if self.juego_terminado: return

        if self.en_pausa:
            self.ventana.after(tiempo_ciclo, self.ciclo_juego)
            return

        tiempo_actual = time.time()
        tiempo_pasado = tiempo_actual - self.tiempo_inicio_juego

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

        for enemigo in self.lista_enemigos:
            old_i, old_j = enemigo.fila_actual, enemigo.columna_actual
            self.restaurar_color_celda(old_i, old_j)
            
            if self.modo == "escapa":
                #persigue al jugador
                enemigo.mover_hacia_jugador(self.jugador.i_pos, self.jugador.j_pos, self.mapa)
            
            elif self.modo == "cazador":
                #huye hacia la salida
                enemigo.mover_hacia_jugador(self.mapa.salida_i, self.mapa.salida_j, self.mapa)
            
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
            
            # MODO CAZADOR: Enemigo llega a la salida
            elif self.modo == "cazador" and casilla.es_salida:
                #el enemigo se esccapó
                self.puntaje -= puntos_escaparon
                if self.puntaje < 0: self.puntaje = 0
                
                #mostrar puntos en el HUD
                puntos_reales = int(self.puntaje * self.factor_dificultad)
                self.lbl_puntaje.config(text=f"Puntaje: {puntos_reales}")
                
                enemigos_a_borrar.append(enemigo)
                self.respawn_enemigo()
            else:
                self.celdas_frames[new_i][new_j].configure(bg=color_enemigo)

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
                    #mostrar puntos en el HUD
                    puntos_reales = int(self.puntaje * self.factor_dificultad)
                    self.lbl_puntaje.config(text=f"Puntaje: {puntos_reales}")
                    
                    self.respawn_enemigo()
            return False

        return False

    def terminar_juego(self, gano):
        """
        Muestra el mensaje y detiene el loop.
        """
        self.juego_terminado = True
        
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