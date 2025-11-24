import time 
import random 
from collections import deque

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

    def intentar_colocar_trampa(self, mapa_obj):
        """
        Intenta colocar una trampa en la posición actual.
        Retorna True si sí pudo.
        """
        tiempo_actual = time.time()

        #verifica el cooldown
        if (tiempo_actual - self.contador_cooldown) < self.cooldown_trampa:
            return False
        
        #verifica la cantidad máxima
        if len(self.trampas_colocadas) >= self.max_trampas_activas:
            return False

        #verifica que no haya ya una trampa ahí
        casilla_actual = mapa_obj.matriz[self.i_pos][self.j_pos]
        if casilla_actual.es_trampa:
            return False
            
        #coloca la trampa
        casilla_actual.es_trampa = True
        self.trampas_colocadas.append((self.i_pos, self.j_pos))
        self.contador_cooldown = tiempo_actual
        return True

    def remover_trampa_de_lista(self, i, j):
        """
        Elimina la trampa de la lista interna para liberar el cupo.
        """
        if (i, j) in self.trampas_colocadas:
            self.trampas_colocadas.remove((i, j))


class Enemigo:
    """
    Clase que controla a los cazadores y su lógica de movimiento.
    """
    def __init__(self, fila_actual, columna_actual, velocidad=0.2):
        self.fila_actual = fila_actual
        self.columna_actual = columna_actual
        self.velocidad = velocidad 
        self.ultimo_movimiento = 0
        
    def mover_hacia_jugador(self, jugador_fila, jugador_columna, mapa_obj):
        """
        El enemigo encuentra el camino más corto evitando los obstáculos.
        """
        tiempo_actual = time.time()
        if (tiempo_actual - self.ultimo_movimiento) < self.velocidad:
            return False

        inicio = (self.fila_actual, self.columna_actual)
        objetivo = (jugador_fila, jugador_columna)
        
        if inicio == objetivo:
            return False

        # Algoritmo para la lógica de movimiento:        
        cola = deque([inicio])       # lista de casillas por visitar
        visitados = set([inicio])    # conjunto de casillas que ya fueron visitadas
        padres = {}                  # Diccionario para reconstruir el camino
        encontrado = False
        
        #bucle de búsqueda
        while cola:
            actual = cola.popleft() #se saca el primero de la fila
            
            if actual == objetivo:
                encontrado = True
                break
            
            fi, co = actual
            
            #se fija en los 4 lados vecinos
            vecinos = [(fi-1, co), (fi+1, co), (fi, co-1), (fi, co+1)]
            random.shuffle(vecinos) 
            
            for vf, vc in vecinos:
                #ve los límites posibles
                if 0 <= vf < mapa_obj.filas and 0 <= vc < mapa_obj.columnas:
                    if (vf, vc) not in visitados:
                        casilla = mapa_obj.matriz[vf][vc]                        
                        es_meta = (vf, vc) == objetivo

                        if casilla.es_accesible_enemigo or es_meta:
                            cola.append((vf, vc))
                            visitados.add((vf, vc))
                            padres[(vf, vc)] = actual
        #reconstruir el camino
        if encontrado:
            paso = objetivo

            while paso in padres and padres[paso] != inicio:
                paso = padres[paso]
            #'paso' se vuelve la casilla a la que deben moverse
            self.fila_actual = paso[0]
            self.columna_actual = paso[1]
            self.ultimo_movimiento = tiempo_actual
            return True 
        return False