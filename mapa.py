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