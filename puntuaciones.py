import os

txt_escapa  = "puntajes_escapa.txt"
txt_cazador = "puntajes_cazador.txt"

def guardar_puntaje(modo, nombre, puntaje):
    """
    Guarda el puntaje en el archivo correspondiente, mantiene solo el top 5.
    """
    archivo = txt_escapa if modo == "escapa" else txt_cazador
    lista = obtener_top_5(modo)
    # agregar un nuevo puntaje
    lista.append((nombre, int(puntaje)))
    # ordenarlos de mayor a menor
    lista.sort(key=lambda x: x[1], reverse=True)    
    # mantener solo los top 5
    lista = lista[:5]
    # guardarlo
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            for nom, pts in lista:
                f.write(f"{nom},{pts}\n")
    except Exception as e:
        print(f"Error al guardar puntaje: {e}")

def obtener_top_5(modo):
    """
    Lee el archivo y retorna una lista con tuplas.
    """
    archivo = txt_escapa if modo == "escapa" else txt_cazador
    lista = []
    
    if not os.path.exists(archivo):
        return []
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")
                if len(datos) == 2:
                    lista.append((datos[0], int(datos[1])))
    except Exception as e:
        print(f"Error al leer puntajes: {e}")
        return []
    return lista