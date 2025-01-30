import ezdxf
import math
import sys

# Recibir rutas como argumentos
input_file = sys.argv[1]
output_file = sys.argv[2]

# Abrir el archivo DXF
doc = ezdxf.readfile(input_file)
msp = doc.modelspace()

# Configuración de capas, colores y grosor de línea
colores_por_patron = {
    "ANSI31": {"border_color": 2, "layer": "PRELOSA_VERDE", "pattern": "ANSI31"},
    "ANSI32": {"border_color": 20, "layer": "PRELOSA_AMARILLA", "pattern": "ANSI32"},
    "ANSI33": {"border_color": 4, "layer": "PRELOSA_ROJA", "pattern": "ANSI33"},
    "ANSI34": {"border_color": 3, "layer": "PRELOSA_AZUL", "pattern": "ANSI34"},
    "ANSI35": {"border_color": 5, "layer": "PRELOSA_MAGENTA", "pattern": "ANSI35"},
    "ANSI36": {"border_color": 6, "layer": "PRELOSA_CYAN", "pattern": "ANSI36"},
    "ANSI37": {"border_color": 18, "layer": "PRELOSA_BLANCO", "pattern": "ANSI37"},
    "AR-B816": {"border_color": 8, "layer": "PRELOSA_AR-B816", "pattern": "AR-B816"},
    "AR-B816C": {"border_color": 9, "layer": "PRELOSA_AR-B816C", "pattern": "AR-B816C"},
    "AR-CONC": {"border_color": 10, "layer": "PRELOSA_AR-CONC", "pattern": "AR-CONC"},
    "AR-HBONE": {"border_color": 11, "layer": "PRELOSA_AR-HBONE", "pattern": "AR-HBONE"},
    "AR-SAND": {"border_color": 12, "layer": "PRELOSA_AR-SAND", "pattern": "AR-SAND"},
    "AR-SQUARE": {"border_color": 13, "layer": "PRELOSA_AR-SQUARE", "pattern": "AR-SQUARE"},
    "BRICK": {"border_color": 14, "layer": "PRELOSA_BRICK", "pattern": "BRICK"},
    "CROSS": {"border_color": 160, "layer": "PRELOSA_CROSS", "pattern": "CROSS"},
    "NET": {"border_color": 16, "layer": "PRELOSA_NET", "pattern": "NET"},
    "ZIGZAG": {"border_color": 17, "layer": "PRELOSA_ZIGZAG", "pattern": "ZIGZAG"},
}

# Patrón por defecto para áreas sin hatch
patron_default = "SOLID"
layer_vacio = "VACIO_ROSADO"
grosor_linea = 50

def activar_capas_temporalmente(doc):
    capas_a_activar = [
        "TyB - PLANTA - TEXTOS GENERALES",
        "TyB - PLANTA - COTAS",
        "TyB - PLANTA - REFUERZOS",
        "TyB - PLANTA - SIMBOLOS",
        "TyB - PLANTA - ENSANCHE",
        "TyB - PLANTA - NIVEL",
        "TyB - GENERAL - VIEWPORT",
        "TyB - CAS - EJES Y COTAS",
    ]
    for layer in capas_a_activar:
        try:
            layer_obj = doc.layers.get(layer)
            layer_obj.on()  # Activa la capa
            print(f"La capa '{layer}' ha sido activada nuevamente.")
        except ezdxf.DXFTableEntryError:
            print(f"La capa '{layer}' no se encontró en el archivo para activarla.")

def activar_patron_ar_sand(doc):
    # Reactivar los objetos HATCH con patrón 'AR-SAND'
    for hatch in doc.modelspace().query('HATCH'):
        if hatch.dxf.pattern_name == "":
            hatch.dxf.pattern_name = "AR-SAND"  # Restaurar el patrón 'AR-SAND'
            print("El patrón 'AR-SAND' ha sido reactivado.")

def desactivar_patron_ar_sand(doc):
    # Desactivar los objetos HATCH con patrón 'AR-SAND'
    for hatch in doc.modelspace().query('HATCH'):
        if hatch.dxf.pattern_name == "AR-SAND":
            hatch.dxf.pattern_name = ""  # Eliminar el patrón 'AR-SAND'

def desactivar_capas_temporalmente(doc):
    capas_a_desactivar = [
        "TyB - PLANTA - TEXTOS GENERALES",
        "TyB - PLANTA - COTAS",
        "TyB - PLANTA - REFUERZOS",
        "TyB - PLANTA - SIMBOLOS",
        "TyB - PLANTA - ENSANCHE",
        "TyB - PLANTA - NIVEL",
        "TyB - GENERAL - VIEWPORT",
        "TyB - CAS - EJES Y COTAS",
    ]
    for layer in capas_a_desactivar:
        try:
            layer_obj = doc.layers.get(layer)
            layer_obj.off()  # Desactiva la capa
            print(f"La capa '{layer}' ha sido desactivada temporalmente.")
        except ezdxf.DXFTableEntryError:
            print(f"La capa '{layer}' no se encontró en el archivo.")

def calcular_area(vertices):
    n = len(vertices)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    return abs(area) / 2.0

def extraer_vertices_de_path(path):
    vertices = []
    if path.type == 1:  # PolylinePath
        vertices = path.vertices
    elif path.type == 2:  # EdgePath
        for edge in path.edges:
            if hasattr(edge, 'start'):
                vertices.append(edge.start)
            if hasattr(edge, 'end'):
                vertices.append(edge.end)
    return vertices

def crear_hatch_con_bordes(msp, vertices, pattern_name, color, layer):
    if len(vertices) < 3:
        return None
    
    hatch = msp.add_hatch(
        color=color, 
        dxfattribs={
            'layer': layer, 
            'pattern_name': pattern_name
        }
    )
    hatch.set_pattern_scale(0.1)
    hatch.append_path(vertices, flags=1)
    hatch.reset_pattern_fill()

    area = calcular_area(vertices)
    if area > 0:
        centroid_x = sum(v[0] for v in vertices) / len(vertices)
        centroid_y = sum(v[1] for v in vertices) / len(vertices)
        msp.add_text(
            f"Área: {area:.2f}",
            dxfattribs={
                'layer': layer,
                'height': 0.2,
                'color': 7
            }
        ).set_dxf_attrib('insert', (centroid_x, centroid_y))

    return hatch


# Ejecutar función para desactivar capas al inicio
desactivar_capas_temporalmente(doc)
desactivar_patron_ar_sand(doc)

# Procesar HATCH existentes
for hatch in msp.query('HATCH'):
    pattern_name = hatch.dxf.pattern_name
    if pattern_name in colores_por_patron:
        color_info = colores_por_patron[pattern_name]
        for path in hatch.paths:
            vertices = extraer_vertices_de_path(path)
            if vertices:
                msp.add_lwpolyline(
                    vertices,
                    close=True,
                    dxfattribs={
                        'color': color_info["border_color"],
                        'layer': color_info["layer"],
                        'lineweight': grosor_linea
                    }
                )
                area = calcular_area(vertices)
                centroid_x = sum(v[0] for v in vertices) / len(vertices)
                centroid_y = sum(v[1] for v in vertices) / len(vertices)
                msp.add_text(
                    f"Área: {area:.2f}",
                    dxfattribs={
                        'layer': color_info["layer"],
                        'height': 0.2,
                        'color': 7
                    }
                ).set_dxf_attrib('insert', (centroid_x, centroid_y))


activar_capas_temporalmente(doc)
activar_patron_ar_sand(doc)

doc.saveas(output_file)

print(f"Archivo procesado y guardado como {output_file}")