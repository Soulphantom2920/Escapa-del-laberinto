import tkinter as tk
import sys
import os
import pygame #para el audio
from juego import JuegoTK
from puntuaciones import obtener_top_5 

# Configuración del menú
color_fondo_menu  = "#1E2E36"
color_texto       = "#FFFFFF"
color_boton       = "#1E2E36" 
color_seleccion   = "#1a466b" 
fuente_titulo     = ("Impact", 55) 
fuente_boton      = ("Arial", 22, "bold")
fuente_texto      = ("Arial", 12)
fuente_tabla      = ("Consolas", 10)

class MenuPrincipal:
    def __init__(self):
        self.raiz = tk.Tk()
        self.raiz.title("Escapa del Laberinto - ¡Also try Adventure!")
        #pantalla completa
        try:
            self.raiz.state("zoomed")
        except:
            self.raiz.attributes("-fullscreen", True)
        self.raiz.configure(bg=color_fondo_menu)

        #música del menú
        self.iniciar_musica_menu()
        #imagen de fondo
        try:
            #busca en recursos
            ruta_fondo = os.path.join("recursos", "fondo_menu.png")
            if os.path.exists(ruta_fondo):
                self.img_fondo = tk.PhotoImage(file=ruta_fondo)
                self.lbl_fondo = tk.Label(self.raiz, image=self.img_fondo)
                self.lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"No se pudo cargar la imagen: {e}")

        # para configuración:
        self.nombre_jugador = tk.StringVar()
        self.dificultad_actual = "facil" 

        # Parte izq del layout:
        self.frame_izquierdo = tk.Frame(self.raiz, bg=color_fondo_menu)
        self.frame_izquierdo.pack(side="left", fill="y", padx=100, pady=130)

        #título
        tk.Label(self.frame_izquierdo, text="ESCAPA DEL\nLABERINTO", bg=color_fondo_menu, fg=color_texto, font=fuente_titulo, justify="left").pack(anchor="w", pady=(0, 60))

        #botones del menú
        self.crear_boton_menu("MODO ESCAPA", self.iniciar_modo_escapa)
        self.crear_boton_menu("MODO CAZADOR", self.iniciar_modo_cazador)
        self.crear_boton_menu("INFO / CONTROLES", self.mostrar_instrucciones)
        self.crear_boton_menu("SALIR", self.salir_del_programa)

        # Parte der del layout:
        self.frame_derecho = tk.Frame(self.raiz, bg=color_fondo_menu)
        self.frame_derecho.pack(side="right", fill="both", expand=True, padx=50, pady=(180, 50))

        #sección del nombre 
        tk.Label(self.frame_derecho, 
                 text="NOMBRE DEL JUGADOR", 
                 bg=color_fondo_menu, fg="#AAAAAA", 
                 font=("Arial", 10, "bold")).pack(pady=(0, 5))
        
        self.entry_nombre = tk.Entry(self.frame_derecho, 
                                     textvariable=self.nombre_jugador, 
                                     font=("Arial", 16), 
                                     bg="#333333", 
                                     fg="white", 
                                     justify="center", 
                                     insertbackground="white")
        
        self.entry_nombre.pack(ipady=5, ipadx=10, fill="x", padx=100)

        #sección de las dificultades 
        tk.Label(self.frame_derecho, 
                 text="SELECCIONAR DIFICULTAD", 
                 bg=color_fondo_menu, 
                 fg="#AAAAAA", 
                 font=("Arial", 10, "bold")).pack(pady=(40,10))
        
        self.frame_dificultad = tk.Frame(self.frame_derecho, bg=color_fondo_menu)
        self.frame_dificultad.pack()

        self.btn_facil = self.crear_boton_dificultad("FÁCIL", "facil", self.frame_dificultad)
        self.btn_medio = self.crear_boton_dificultad("MEDIO", "medio", self.frame_dificultad)
        self.btn_dificil = self.crear_boton_dificultad("DIFÍCIL", "dificil", self.frame_dificultad)
        
        self.actualizar_botones_dificultad() 

        # Tablas de puntajes:
        tk.Label(self.frame_derecho, 
                 text="MEJORES PUNTAJES", 
                 bg=color_fondo_menu, 
                 fg="#AAAAAA", 
                 font=("Arial", 14, "bold")).pack(pady=(60, 20))
        
        self.frame_tablas = tk.Frame(self.frame_derecho, bg=color_fondo_menu)
        self.frame_tablas.pack(fill="x", padx=20)

        #tabla de Escapa
        self.frame_tabla_escapa = tk.Frame(self.frame_tablas, 
                                           bg="#222222", 
                                           bd=2, 
                                           relief="flat")
        
        self.frame_tabla_escapa.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(self.frame_tabla_escapa, 
                 text="TOP 5 - ESCAPA", 
                 bg="#333333", 
                 fg="white", 
                 font=("Arial", 10, "bold")).pack(fill="x", ipady=5)
        
        self.lbl_lista_escapa = tk.Label(self.frame_tabla_escapa, 
                                         text="...", 
                                         bg="#222222", 
                                         fg="#CCCCCC", 
                                         font=fuente_tabla, 
                                         justify="left")
        
        self.lbl_lista_escapa.pack(pady=10)

        #tabla de Cazador
        self.frame_tabla_cazador = tk.Frame(self.frame_tablas, 
                                            bg="#222222", 
                                            bd=2, relief="flat")
        
        self.frame_tabla_cazador.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(self.frame_tabla_cazador, 
                 text="TOP 5 - CAZADOR", 
                 bg="#333333", 
                 fg="white",
                 font=("Arial", 10, "bold")).pack(fill="x", ipady=5)
        
        self.lbl_lista_cazador = tk.Label(self.frame_tabla_cazador, 
                                          text="...", 
                                          bg="#222222", 
                                          fg="#CCCCCC", 
                                          font=fuente_tabla, 
                                          justify="left")
        
        self.lbl_lista_cazador.pack(pady=10)
        
        self.cargar_tablas_puntajes()

    def iniciar_musica_menu(self):
        """Inicializa pygame y reproduce la música de fondo."""
        try:
            pygame.mixer.init()
            ruta = os.path.join("recursos", "musica_menu_prin.mp3") 
            if os.path.exists(ruta):
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.play(-1) #loop infinito
                pygame.mixer.music.set_volume(0.4)
        except Exception as e:
            print(f"No se pudo reproducir música: {e}")

    def crear_boton_menu(self, texto, comando, estado="normal"):
        color_fg = color_texto
        if estado == "disabled":
            color_fg = "#555555"

        btn = tk.Button(self.frame_izquierdo, text=texto, 
                        font=fuente_boton, bg=color_boton, fg=color_fg,
                        activebackground=color_seleccion, activeforeground=color_texto,
                        bd=0, relief="flat", cursor="hand2",
                        state=estado, command=comando, anchor="w", padx=20)

        btn.pack(fill="x", pady=10)
        
        if estado == "normal":
            btn.bind("<Enter>", lambda e: btn.config(bg=color_seleccion))
            btn.bind("<Leave>", lambda e: btn.config(bg=color_boton))

    def crear_boton_dificultad(self, texto, valor, padre):
        btn = tk.Button(padre, text=texto, font=("Arial", 10, "bold"),
                        bg=color_boton, fg="white", width=10,
                        bd=1, relief="solid", cursor="hand2",
                        command=lambda: self.set_dificultad(valor))
        btn.pack(side="left", padx=5)
        return btn

    def set_dificultad(self, valor):
        self.dificultad_actual = valor
        self.actualizar_botones_dificultad()
        self.cargar_tablas_puntajes()

    def actualizar_botones_dificultad(self):
        btns = {"facil": self.btn_facil, "medio": self.btn_medio, "dificil": self.btn_dificil}
        for x, btn in btns.items():
            if x == self.dificultad_actual:
                btn.config(bg=color_seleccion)
            else:
                btn.config(bg=color_boton)

    def validar_inicio(self):
        nombre = self.nombre_jugador.get().strip()
        if not nombre:
            self.entry_nombre.config(bg="#550000") 
            self.raiz.after(500, lambda: self.entry_nombre.config(bg="#333333"))
            return False
        return True

    def iniciar_modo_escapa(self):
        if not self.validar_inicio(): return
        self.raiz.withdraw() 
        JuegoTK(modo="escapa", 
                dificultad=self.dificultad_actual, 
                nombre_jugador=self.nombre_jugador.get().strip(), 
                callback_volver=self.mostrar_menu)

    def iniciar_modo_cazador(self):
        if not self.validar_inicio(): return
        self.raiz.withdraw()
        JuegoTK(modo="cazador", 
                dificultad=self.dificultad_actual, 
                nombre_jugador=self.nombre_jugador.get().strip(),
                callback_volver=self.mostrar_menu)

    def mostrar_menu(self):
        self.raiz.deiconify()
        self.cargar_tablas_puntajes() 
        #al volver se reinicia la música del menú
        self.iniciar_musica_menu()
        
        try:
            self.raiz.state("zoomed")
        except:
            self.raiz.attributes("-fullscreen", True)

    def cargar_tablas_puntajes(self):
        def formatear_lista(datos):
            if not datos: return "Sin registros"
            texto = ""
            for i, (nom, pts) in enumerate(datos, 1):
                texto += f"{i}. {nom:<12} {pts}\n"
            return texto

        top_escapa = obtener_top_5("escapa", self.dificultad_actual)
        top_cazador = obtener_top_5("cazador", self.dificultad_actual)

        self.lbl_lista_escapa.config(text=formatear_lista(top_escapa))
        self.lbl_lista_cazador.config(text=formatear_lista(top_cazador))

    def mostrar_instrucciones(self):
        """
        Muestra una ventanita emergente con la información de juego y los controles.
        """
        ventana_ayuda = tk.Toplevel(self.raiz)
        ventana_ayuda.title("Instrucciones de Juego")
        ventana_ayuda.geometry("650x650")
        ventana_ayuda.configure(bg="#222222")
        ventana_ayuda.resizable(False, False)

        #centrar la ventana
        ancho_pantalla = self.raiz.winfo_screenwidth()
        alto_pantalla = self.raiz.winfo_screenheight()
        x = (ancho_pantalla//2) - (300)
        y = (alto_pantalla//2) - (275)
        ventana_ayuda.geometry(f"600x550+{x}+{y}")

        #Titulo
        tk.Label(ventana_ayuda, text="¿CÓMO JUGAR?", 
                 bg="#222222", fg="#FFD700", 
                 font=("Impact", 30)).pack(pady=(20, 10))

        #controles
        texto_controles = ("--- CONTROLES ---\n\n"
                           "MOVIMIENTO:  [W] [A] [S] [D]\n"
                           "CORRER:  [SHIFT] (Consume tu Energía)\n"
                           "PONER TRAMPA:  [ESPACIO] (Solo para modo Escapa)\n"
                           "PAUSA:  [ESC]\n")
        tk.Label(ventana_ayuda, text=texto_controles, 
                 bg="#222222", fg="white", 
                 font=("Consolas", 14, "bold"), justify="center").pack(pady=10)

        #separador de la info
        tk.Frame(ventana_ayuda, bg="#555555", height=2, width=500).pack(pady=10)

        #explicación de los modos
        texto_modos = ("--- MODO ESCAPA ---\n\n"
                       "Objetivo: llegar a la salida (casilla amarilla).\n"
                       "Evita a los cazadores (Rojos) o usa trampas para detenerlos un momento.\n"
                       "Cuida tu energía, al correr se gasta\n\n"
                       "--- MODO CAZADOR --- \n\n"
                       "Te vuelves el cazador, atrapa a los enemigos antes de que\n"
                       "lleguen a la salida. Si escapan, pierdes puntos.\n"
                       "Consigue el mayor puntaje antes de que acabe el tiempo")
        tk.Label(ventana_ayuda, text=texto_modos, 
                 bg="#222222", fg="#CCCCCC", 
                 font=("Arial", 11), justify="center").pack(pady=10)
        
        #botón para cerrar
        btn_cerrar = tk.Button(ventana_ayuda, text="OK", 
                               font=("Arial", 11, "bold"),
                               bg=color_boton, fg="white",
                               activebackground=color_seleccion,
                               bd=0, cursor="hand2",
                               command=ventana_ayuda.destroy)
        btn_cerrar.pack(pady=20, ipadx=20, ipady=5)

    def salir_del_programa(self):
        self.raiz.destroy()
        sys.exit()

    def iniciar(self):
        self.raiz.mainloop()
        

if __name__ == "__main__":
    app = MenuPrincipal()
    app.iniciar()