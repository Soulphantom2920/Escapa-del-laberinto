import random

class Casilla:
    """
    Clase padre para todos terrenos.
    """
    def __init__(self):
        self.es_accesible_jugador = True
        self.es_accesible_enemigo = True
        self.es_salida = False
        self.es_trampa = False
        self.tipo = "camino" 

class Camino(Casilla):
    """
    Terreno accesible para ambos.
    """
    pass 

class Muro(Casilla):
    """
    Terreno inaccesible.
    """
    def __init__(self):
        self.es_accesible_jugador = False
        self.es_accesible_enemigo = False
        self.es_salida = False
        self.es_trampa = False
        self.tipo = "muro"

class Liana(Casilla):
    """
    Terreno accesible solo para enemigos.
    """
    def __init__(self):
        self.es_accesible_jugador = False
        self.es_accesible_enemigo = True
        self.es_salida = False
        self.es_trampa = False
        self.tipo = "liana"

class Tunel(Casilla):
    """
    Terreno accesible solo para el jugador.
    """
    def __init__(self):
        self.es_accesible_jugador = True
        self.es_accesible_enemigo = False
        self.es_salida = False
        self.es_trampa = False
        self.tipo = "tunel"

class Mapa:
    """
    Contiene la matriz del juego y la lógica para generarla de forma aleatoria.
    """
    def __init__(self, filas, columnas):
        self.filas = filas
        if filas % 2 == 0:
            self.filas = filas - 1 

        self.columnas = columnas
        if columnas % 2 == 0:
            self.columnas = columnas - 1
        
        self.matriz = [] 
        self.inicio_i = 1
        self.inicio_j = 1
        self.salida_i = 0
        self.salida_j = 0
        
        self.generar_laberinto()

    def generar_laberinto(self):
        """
        Da paso a la creación del mapa.
        """
        # Llena todo de muros
        self.matriz = []
        for i in range(self.filas):
            fila = []
            for j in range(self.columnas):
                fila.append(Muro())
            self.matriz.append(fila)

        # Crea los caminos principales
        self.excavar_camino(1, 1)
        
        # Romper muros extra para dejar espacios abiertos 
        self.crear_habitaciones()

        # Añade las lianas y túneles
        self.colocar_terrenos_especiales()

        # Coloca la salida y el inicio
        self.colocar_salida()
        self.colocar_inicio()

    def excavar_camino(self, i, j):
        """
        Algoritmo recursivo que hace los caminos.
        """
        self.matriz[i][j] = Camino() 

        direcciones = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(direcciones) 

        for di, dj in direcciones:
            ni = i + di
            nj = j + dj 
            
            if 1 <= ni < self.filas - 1 and 1 <= nj < self.columnas - 1:
                if self.matriz[ni][nj].tipo == "muro":
                    muro_i = i + (di // 2)
                    muro_j = j + (dj // 2)
                    self.matriz[muro_i][muro_j] = Camino()
                    self.excavar_camino(ni, nj)

    def crear_habitaciones(self):
        """
        Abre algunos muros para crear habitaciones.
        """
        probabilidad = 0.10 
        for i in range(1, self.filas - 1):
            for j in range(1, self.columnas - 1):
                if self.matriz[i][j].tipo == "muro":
                    if i % 2 == 0 or j % 2 == 0:
                        if random.random() < probabilidad:
                            self.matriz[i][j] = Camino()

    def colocar_terrenos_especiales(self):
        """
        Convierte algunos muros en lianas o túneles.
        """
        #probabilidades 
        chance_liana = 0.03  
        chance_tunel = 0.03 

        for i in range(1, self.filas- 1):
            for j in range(1, self.columnas- 1):
                #solo reemplaza los muros internos, no los bordes 
                if self.matriz[i][j].tipo == "muro":
                    bateo = random.random()
                    if bateo < chance_liana:
                        self.matriz[i][j] = Liana()
                    elif bateo < (chance_liana + chance_tunel):
                        self.matriz[i][j] = Tunel()

    def colocar_salida(self):
        """
        Coloca la salida en un borde.
        """
        lados = ["arriba", "abajo", "izquierda", "derecha"]
        while True:
            lado = random.choice(lados)
            i, j = 0, 0
            if lado == "arriba": i, j = 0, random.randrange(1, self.columnas - 1)
            elif lado == "abajo": i, j = self.filas - 1, random.randrange(1, self.columnas - 1)
            elif lado == "izquierda": i, j = random.randrange(1, self.filas - 1), 0
            elif lado == "derecha": i, j = random.randrange(1, self.filas - 1), self.columnas - 1

            #verificar 
            tiene_camino = False
            vecinos = [(-1,0), (1,0), (0,-1), (0,1)]
            for vi, vj in vecinos:
                vec_i, vec_j = i + vi, j + vj
                if 0 <= vec_i < self.filas and 0 <= vec_j < self.columnas:
                    if self.matriz[vec_i][vec_j].tipo == "camino":
                        tiene_camino = True
                        break
            if tiene_camino:
                self.salida_i = i
                self.salida_j = j
                self.matriz[i][j] = Camino()
                self.matriz[i][j].es_salida = True
                break 

    def colocar_inicio(self):
        """
        Coloca al jugador lejos de la salida.
        """
        max_distancia = -1
        mejor_i, mejor_j = 1, 1
        candidatos = [(1, 1), (1, self.columnas-2), (self.filas-2, 1), (self.filas-2, self.columnas-2)]

        for i, j in candidatos:
            if i < self.filas and j < self.columnas:
                dist = abs(i - self.salida_i) + abs(j - self.salida_j)
                if dist > max_distancia:
                    max_distancia = dist
                    mejor_i, mejor_j = i, j
        
        self.inicio_i = mejor_i
        self.inicio_j = mejor_j
        self.matriz[mejor_i][mejor_j] = Camino()

    def colocar_terrenos_especiales(self):
        """
        Convierte algunos muros en lianas o túneles, solo si tiene dos muros 
        a la izq y der o arriba y abajo para que sean puentes.
        """
        # probabilidades 
        chance_liana = 0.04  
        chance_tunel = 0.04 

        for i in range(1, self.filas- 1):
            for j in range(1, self.columnas- 1):
                #no reemplaza bordes 
                if self.matriz[i][j].tipo == "muro":
                    #revisar si cumple
                    util = self.ver_utilidad_muro(i, j)

                    if util:
                        bateo = random.random()
                        if bateo < chance_liana:
                            self.matriz[i][j] = Liana()
                        elif bateo < (chance_liana+chance_tunel):
                            self.matriz[i][j] = Tunel()

    def ver_utilidad_muro(self, i, j):
        """
        Verifica si el muro está entre dos muros en el mismo eje.
        E: Coordenadas del muro.
        S: True si es un puente válido.
        """
        es_horizontal = (self.matriz[i][j-1].tipo == "muro" and self.matriz[i][j+1].tipo == "muro")
        es_vertical = (self.matriz[i-1][j].tipo == "muro" and self.matriz[i+1][j].tipo == "muro")
        
        return es_horizontal or es_vertical
        