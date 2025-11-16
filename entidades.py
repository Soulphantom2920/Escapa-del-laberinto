class Jugador:
    """
    Controla el estado y la lógica del personaje del jugador.
    """
    def __init__(self, i_pos, j_pos):
        # Posiciones en la matriz
        self.i_pos = i_pos
        self.j_pos = j_pos

        # Atributos de la energía
        self.energia_max = 100
        self.energia_actual = self.energia_max

        # Atributos de las trampas
        self.max_trampas_activas = 3
        self.trampas_colocadas = [] # Para las coordenadas (i, j)
        self.cooldown_trampa = 5 # Segundos de enfriamiento
        self.contador_cooldown = 0 