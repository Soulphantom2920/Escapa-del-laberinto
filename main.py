import tkinter as tk
import sys
from juego import JuegoTK

# Configuración del menú
color_fondo_menu  = "#1A1A1A"
color_texto       = "#FFFFFF"
color_boton       = "#1A1A1A" 
color_boton_tocar = "#333333"
fuente_titulo     = ("Impact", 55) 
fuente_boton      = ("Arial", 22, "bold")

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

        #layout izq
        self.frame_izquierdo = tk.Frame(self.raiz, bg=color_fondo_menu)
        self.frame_izquierdo.pack(side="left", fill="y", padx=100, pady=130)

        #título
        tk.Label(self.frame_izquierdo, text="ESCAPA DEL\nLABERINTO", bg=color_fondo_menu, fg=color_texto, font=fuente_titulo, justify="left").pack(anchor="w", pady=(0, 60))

        #botones del menú
        self.crear_boton_menu("MODO ESCAPA", self.iniciar_modo_escapa)
        self.crear_boton_menu("MODO CAZADOR", None, estado="disabled")
        self.crear_boton_menu("SALIR", self.salir_del_programa)

    def crear_boton_menu(self, texto, comando, estado="normal"):
        color_fg = color_texto
        if estado == "disabled":
            color_fg = "#555555"

        btn = tk.Button(self.frame_izquierdo, text=texto, 
                        font=fuente_boton, bg=color_boton, fg=color_fg,
                        activebackground=color_boton_tocar, activeforeground=color_texto,
                        bd=0, relief="flat", cursor="hand2",
                        state=estado, command=comando, anchor="w", padx=20)

        btn.pack(fill="x", pady=10)
        
        if estado == "normal":
            btn.bind("<Enter>", lambda e: btn.config(bg=color_boton_tocar))
            btn.bind("<Leave>", lambda e: btn.config(bg=color_boton))

    def iniciar_modo_escapa(self):
        self.raiz.withdraw() 
        JuegoTK(callback_volver=self.mostrar_menu)

    def mostrar_menu(self):
        """Devuelve la ventana del menú."""
        self.raiz.deiconify()
        try:
            self.raiz.state("zoomed")
        except:
            self.raiz.attributes("-fullscreen", True)

    def salir_del_programa(self):
        self.raiz.destroy()
        sys.exit()

    def iniciar(self):
        self.raiz.mainloop()
        

if __name__ == "__main__":
    app = MenuPrincipal()
    app.iniciar()