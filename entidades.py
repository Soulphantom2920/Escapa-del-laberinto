import time # para la velocidad de movimiento

class Jugador:
    """
    Controla el estado y la lógica del personaje del jugador.
    """
    def __init__(self, i_pos, j_pos):
        # Posiciones en la matriz
        self.i_pos = i_pos
        self.j_pos = j_pos

        # Atributos de la energía
        self.energia_max = 100.0
        self.energia_actual = self.energia_max
        self.esta_corriendo = False # para saber si corre o camina

        # Atributos de las trampas
        self.max_trampas_activas = 3
        self.trampas_colocadas = [] # Para las coordenadas (i, j)
        self.cooldown_trampa = 5 # Segundos de enfriamiento
        self.contador_cooldown = 0 

        # Control de la velocidad 
        self.ultimo_movimiento = 0
        self.velocidad_caminar = 0.1  # Segundos al caminar
        self.velocidad_correr = 0.05  # Segundos al correr 

    def intentar_mover(self, cambio_fila, cambio_columna, mapa_obj):
        """
        Intenta mover al jugador validando las colisiones y el tiempo.
        E: El cambio en la fila y columna hacia donde se quiere ir, y el objeto mapa.
        S: True si se movió, False si no.
        """
        # Control de la velocidad
        tiempo_actual = time.time()
        espera_necesaria = self.velocidad_correr if self.esta_corriendo else self.velocidad_caminar

        if tiempo_actual - self.ultimo_movimiento < espera_necesaria:
            return False # No se mueve hasta que pase el tiempo
            
        # Verificar los limites de la matriz
        nueva_i = self.i_pos + cambio_fila
        nueva_j = self.j_pos + cambio_columna
        
        if not (0 <= nueva_i < mapa_obj.filas and 0 <= nueva_j < mapa_obj.columnas):
            return False

        # Verificar si la casilla es accesible 
        casilla_destino = mapa_obj.matriz[nueva_i][nueva_j]
        
        if casilla_destino.es_accesible_jugador:
            self.i_pos = nueva_i
            self.j_pos = nueva_j
            self.ultimo_movimiento = tiempo_actual 
            return True
        else:
            return False

    def gestionar_energia(self, se_movio):
        """
        Controla el gasto y recuperación de energía.
        E: Booleano que indica si el personaje se movió en el ciclo.
        S: *atributos modificados.
        """
        if self.esta_corriendo and se_movio:
            self.energia_actual -= 2.0 # gasta la energía al correr
            if self.energia_actual <= 0:
                self.energia_actual = 0
                self.esta_corriendo = False # se cansa y deja de correr
        else:
            # recupera energía si no corre 
            if self.energia_actual < self.energia_max:
                self.energia_actual += 0.5

                