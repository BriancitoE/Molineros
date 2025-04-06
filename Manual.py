
# MANUAL DETALLADO DEL CÓDIGO PYTHON PARA MODELADO Y VISUALIZACIÓN DE LA DISPERSIÓN 
# DE CONTAMINANTES EN CUERPOS DE AGUA USANDO ArcGIS

# PRIMERO, IMPORTAMOS TODAS LAS LIBRERIAS QUE NECESITAMOS 

"""
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import Modulo1, Modulo2, Modulo3, Modulo4
import arcpy

¿Qué hace cada línea?
   import numpy as np: Importa la librería NumPy, fundamental para manejar matrices 
   y arreglos numéricos, que se usarán para representar la concentración del contaminante 
   en el cuerpo de agua.

   import geopandas as gpd: Importa GeoPandas, una herramienta poderosa para manejar datos
   geoespaciales tipo vector. Aunque en tu código actual no se usa directamente, probablemente 
   esté destinado a manipular shapefiles o datos espaciales más adelante.

   import matplotlib.pyplot as plt: Importa Matplotlib, que sirve para graficar. 
   Puede usarse más adelante para visualizar los resultados del modelo fuera de ArcGIS.

   import Modulo1, Modulo2, Modulo3, Modulo4: Estos son tus propios archivos .py que contienen
   funciones organizadas por módulos. Aquí estás haciendo disponibles las funciones de cada módulo.

   import arcpy: Importa ArcPy, el módulo de Python para trabajar con ArcGIS Pro. Es esencial para
   crear capas, raster, campos, hacer interpolaciones, etc.
"""
# MÓDULO 1: INSERCIÓN Y ACTUALIZACIÓN DE MATRIZ DE CONCENTRACIÓN
"""

1. insertar_datos(datos_de_entrada)
Esta función inicializa todas las variables necesarias y crea una matriz 2D que representa el cuerpo 
de agua. También simula un vertimiento puntual en la matriz.

Parámetros esperados:
datos_de_entrada = {
  "tamaño de celda x": 1,
  "tamaño de celda y": 1,
  "dt": 1,
  "caudal m3/s": 1,
  "concentracion mg/l": 300,
  ...
}

Explicación paso por paso:
- Se extraen variables del diccionario.
- Se crea una matriz de ceros m con tamaño Lx por Ly.
- Se inserta un valor o valores de concentración en una celda o celdas específica (a, b) simulando el o los 
  vertimientos que puedan estar presentes en el cuerpo de agua léntico. 
La fórmula:
m[a, b] = (q * concen_vertimiento / (dx * dy)) * dt
Representa la masa de contaminante (en mg) que se vierte por unidad de área por unidad de tiempo.

2. actualizar_conce(...)
Esta función simula la dispersión del contaminante aplicando una versión de la ecuación de advección-difusión 
en 2D. La ecuacuón de advección y difusión está resuelta por método de diferencias finitas.

¿Qué se calcula?
Para cada celda (i,j) excepto los bordes, se calcula:

Advección (transporte por el flujo del agua):
adv_x = -ux * (m[i, j] - m[i-1, j]) / dx
adv_y = -uy * (m[i, j] - m[i, j-1]) / dy

Difusión (dispersión del contaminante):
diff_x = d_x * (m[i+1, j] - 2*m[i, j] + m[i-1, j]) / dx**2
diff_y = d_y * (m[i, j+1] - 2*m[i, j] + m[i, j-1]) / dy**2

Degradación (pérdida de concentración):
-k * m[i,j]
Y se actualiza la celda usando diferencias finitas explícitas:
m[i, j] = m[i, j] + dt * (adv_x + adv_y + diff_x + diff_y - k * m[i, j])

3. Finalmente, el vertimiento se vuelve a aplicar en cada iteración:
m[a,b] += (q * concen_vertimiento / (dx * dy)) * dt
"""

#MÓDULO 2: CREACIÓN Y POBLACIÓN DE UN FEATURE CLASS
"""
1. feature_class(nombre, gdb)
Esta función crea una capa de puntos (Feature Class) con sistema de coordenadas UTM Zona 18S dentro de un geodatabase en ArcGIS.

Utiliza arcpy.management.CreateFeatureclass.
El sistema de coordenadas se establece usando una cadena de proyección completa (zona UTM 18S del sur del Perú).
Devuelve la ruta del feature class creado, por ejemplo:
"C:\\proyecto\\geodatabase.gdb\\puntos_concentracion"

2. plotear_arreglo(zona_vertimiento, x0, y0, Lx, Ly, dx, dy, m)
Esta función: 
- Añade un campo concen de tipo DOUBLE.
- Recorre cada celda del arreglo m y convierte sus valores a puntos espaciales (X, Y) según coordenadas UTM.
- Usa un InsertCursor para insertar cada punto con su valor de concentración.
x = x0 + i * dx
y = y0 + j * dy
cursor.insertRow([(x, y), m[i, j]])
Esto permite que ArcGIS visualice el campo de concentración como puntos dispersos.
"""

#MÓDULO 3: INTERPOLACIÓN Y CLASIFICACIÓN RASTER
"""
1. interpolacion(nombre, gdb, nombre_salida)
- arcpy.ddd.Idw(nombre, "concen", salida, 0.1, 6, "VARIABLE 12", None)
  Genera un raster interpolado a partir del feature class usando el método IDW (Inverse Distance Weighting).
  "concen" es el campo que se interpolará.
  "VARIABLE 12" significa que se considera una vecindad variable de hasta 12 puntos.
- Luego devuelve un raster que representa la distribución espacial continua de la concentración del contaminante.

2. reclass(raster, clases, Eca)
Genera una expresión de reclasificación basada en la concentración interpolada, utilizando un patrón geométrico 
exponencial.
- Determina el valor mínimo y máximo del raster.
- Usa el valor de ECA (Estándar de Calidad Ambiental) como el primer límite.
- Calcula una razón geométrica r que permite construir clases de la forma:
0-ECA, ECA-ECA*r, ECA*r-ECA*r², ..., hasta cubrir el máximo.
Devuelve una cadena de reclasificación que se puede usar en arcpy.sa.Reclassify.
Ejemplo:
0 50 50; 50 75 75; 75 112 112; 112 168 168;

3. reclassify (nombre,reclasificacion,gdb, nombre_salida):
Aplica los rangos establecidos al raster previamente establecidos


"""
#MÓDULO 4: Crear y suavizar polígonos
"""
1. def polygon (nombre,gdb,nombre_salida, Eca):
Crea un polígono a partir del raster interpolado y reclasificado previamente
- arcpy.RasterToPolygon_conversion(nombre, gdb + "\\" + nombre_salida, "true", "Value")
  Transforma el raster reclasificado en un polígono.
- arcpy.MakeFeatureLayer_management(nombre_salida, "poligono")
  Crea una capa temporal para seleccionar los registros
- arcpy.SelectLayerByAttribute_management("poligono", "NEW_SELECTION", f'"gridcode" = {Eca}')
  Selecciona los polígonos con gridcode = 5
- arcpy.DeleteFeatures_management("poligono")
  Se eliminan los polígonos que están en el nivel aceptable (igual al ECA).
"gridcode" es el campo generado que contiene los valores de clase del raster.
- Al final obtenemos el nombre de la capa poligonal filtrada (solo con valores superiores al ECA).

2. suavizado (nombre,gdb,nombre_salida):   
Crea unSuavizado del polígono
- arcpy.SmoothPolygon_cartography(nombre, gdb + "\\" + nombre_salida, "PAEK", "10 Meters", "FIXED_ENDPOINT", "NO_CHECK")
  Suaviza los bordes del polígono:
  "PAEK": Método de suavizado geométrico.
  "10 Meters": Tolerancia del suavizado.
  "FIXED_ENDPOINT": Conserva los puntos finales del polígono.
- Al final devuelve el nombre del polígono suavizado listo para visualizar o usar en mapas.


"""