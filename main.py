from juego import JuegoTK

def main():
    """
    Función principal que inicia la aplicación.
    """
    # Por ahora, solo se comienza el juego directamente.
    # Después aquí podría ir la ventana para el registro.

    app = JuegoTK()
    app.iniciar()

# Para que solo se ejecute cuando se ejecuta main
if __name__ == "__main__":
    main()