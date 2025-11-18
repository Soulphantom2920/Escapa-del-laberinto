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
    Terreno accesible para ambos, hereda todo de Casilla.
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
    Contiene la matriz del juego y la logica para generarla.
    """
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        
        self.matriz = [] 
        
        # crea el mapa estatico
        self.generar_mapa_estatico()

    def generar_mapa_estatico(self):
        """
        Crea una matriz básica con con un borde de muro y un centro de camino.
        """
        self.matriz = []
        
        for i in range(self.filas):
            fila_actual = [] 
            for j in range(self.columnas):
                # Para saber si está en el borde o en el centro:
                if (i == 0 or i == (self.filas - 1) or j == 0 or j == (self.columnas - 1)):                    
                    fila_actual.append(Muro())
                else:
                    fila_actual.append(Camino())
            self.matriz.append(fila_actual) #Añadir la fila completa
