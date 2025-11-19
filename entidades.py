import time 

class Jugador:
    """
    Controla el estado y la lógica del personaje del jugador.
    """
    def __init__(self, i_pos, j_pos):
        # Posiciones en la matriz
        self.i_pos = i_pos
        self.j_pos = j_pos

        # Energía
        self.energia_max = 100.0
        self.energia_actual = self.energia_max
        self.esta_corriendo = False 
        
        self.en_fatiga = False # Si True, hay que recargar energía

        # Trampas
        self.max_trampas_activas = 3
        self.trampas_colocadas = [] 
        self.cooldown_trampa = 5 
        self.contador_cooldown = 0 

        # Velocidad
        self.ultimo_movimiento = 0
        self.velocidad_caminar = 0.1  
        self.velocidad_correr = 0.05   

    def intentar_mover(self, cambio_fila, cambio_columna, mapa_obj):
        """
        Intenta mover al jugador validando tiempo y colisiones.
        """
        tiempo_actual = time.time()
        
        # Determinar la velocidad actual
        espera = self.velocidad_caminar
        if self.esta_corriendo and not self.en_fatiga:
            espera = self.velocidad_correr
        
        # Cooldown del movimiento
        if tiempo_actual - self.ultimo_movimiento < espera:
            return False 
            
        nueva_i = self.i_pos + cambio_fila
        nueva_j = self.j_pos + cambio_columna
        
        # Verificar los límites
        if not (0 <= nueva_i < mapa_obj.filas and 0 <= nueva_j < mapa_obj.columnas):
            return False

        # Verificar los muros
        casilla_destino = mapa_obj.matriz[nueva_i][nueva_j]
        
        if casilla_destino.es_accesible_jugador:
            self.i_pos = nueva_i
            self.j_pos = nueva_j
            self.ultimo_movimiento = tiempo_actual 
            return True
        else:
            return False

    def actualizar_correr(self, quiere_correr):
        """
        Recibe el input del teclado y ve cómo actúa según la barra de energía
        """
        if self.en_fatiga:
            self.esta_corriendo = False 
        elif quiere_correr and self.energia_actual > 0:
            self.esta_corriendo = True
        else:
            self.esta_corriendo = False

    def manejar_energia(self, se_movio):
        """
        Controla el gasto y recuperación de energia.
        """
        # Recuperación de energía
        if not self.esta_corriendo or self.en_fatiga:
            if self.energia_actual < self.energia_max:
                self.energia_actual += 0.5

            # Deja de estar fatigado
            if self.energia_actual >= self.energia_max:
                self.energia_actual = self.energia_max
                self.en_fatiga = False 

        # Gasto de energía
        elif self.esta_corriendo and se_movio and not self.en_fatiga:
            self.energia_actual -= 1.0 
            
            # Si llega a 0, entra en cansansio 
            if self.energia_actual <= 0:
                self.energia_actual = 0
                self.en_fatiga = True
                self.esta_corriendo = False 