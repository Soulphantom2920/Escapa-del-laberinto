import tkinter as tk
import sys
from juego import JuegoTK
from puntuaciones import obtener_top_5 

# Configuración del menú
color_fondo_menu  = "#1A1A1A"
color_texto       = "#FFFFFF"
color_boton       = "#1A1A1A" 
color_seleccion   = "#555555" 
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

        top_escapa = obtener_top_5("escapa")
        top_cazador = obtener_top_5("cazador")

        self.lbl_lista_escapa.config(text=formatear_lista(top_escapa))
        self.lbl_lista_cazador.config(text=formatear_lista(top_cazador))

    def salir_del_programa(self):
        self.raiz.destroy()
        sys.exit()

    def iniciar(self):
        self.raiz.mainloop()
        

if __name__ == "__main__":
    app = MenuPrincipal()
    app.iniciar()