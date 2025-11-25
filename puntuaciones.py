import os

txt_escapa  = "puntajes_escapa.txt"
txt_cazador = "puntajes_cazador.txt"

def guardar_puntaje(modo, nombre, puntaje, dificultad):
    """
    Guarda el puntaje en el archivo correspondiente, mantiene solo el top 5.
    """
    archivo = txt_escapa if modo == "escapa" else txt_cazador
    
    #leemos todos los datos
    todos_registros = []
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    datos = linea.strip().split(",")
                    if len(datos) == 3: # Aseguramos que tenga los 3 datos
                        todos_registros.append((datos[0], int(datos[1]), datos[2]))
        except:
            pass

    #agrega el nuevo puntaje
    todos_registros.append((nombre, int(puntaje), dificultad))
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            for nom, pts, dif in todos_registros:
                f.write(f"{nom},{pts},{dif}\n")
    except Exception as e:
        print(f"Error al guardar puntaje: {e}")

def obtener_top_5(modo, dificultad_filtro):
    """
    Retorna el Top 5 filtrado por la dificultad seleccionada.
    """
    archivo = txt_escapa if modo == "escapa" else txt_cazador
    lista_filtrada = []
    
    if not os.path.exists(archivo):
        return []
    
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")
                if len(datos) == 3:
                    nom, pts, dif = datos[0], int(datos[1]), datos[2]
                    # Solo se agrega si coincide con la dificultad del menú
                    if dif == dificultad_filtro:
                        lista_filtrada.append((nom, pts))
    except Exception as e:
        print(f"Error al leer puntajes: {e}")
        return []

    #ordena de mayor a menor y toma los top 5 
    lista_filtrada.sort(key=lambda x: x[1], reverse=True)
    return lista_filtrada[:5]