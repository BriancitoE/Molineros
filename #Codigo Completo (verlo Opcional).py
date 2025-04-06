
#Proyectozonademezcla
#Importamos librerias necesarias
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import arcpy

#Para una primera etapa asumimremos valores
datos_de_entrada = {"tamaño de celda x":1, 
                    "tamaño de celda y":1,
                    "dt":1,
                    "caudal m3/s":5,
                    "concentracion mg/l":300,
                    "velocidad de flujo x":0.2,
                    "velocidad de flujo y":0.2,
                    "coef de difusion x":0.01,
                    "coef de difusion y":0.01,
                    "coef de degradacion":0.01,
                    "amplitud x":200,
                    "amplitud y":200,
                    "ubicacion del vertimiento en x":20,
                    "ubicacion del vertimiento en y":100}
dx = datos_de_entrada["tamaño de celda x"] #tamaño de la celda
dy = datos_de_entrada["tamaño de celda y"] #tamaño de la celda
dt = datos_de_entrada["dt"] #seg
q = datos_de_entrada["caudal m3/s"] #m3/s
concen_vertimiento = datos_de_entrada["concentracion mg/l"] #mg/L SST
ux = datos_de_entrada["velocidad de flujo x"] #velocidad del flujo en m/s
uy = datos_de_entrada["velocidad de flujo y"] #velocidad del flujo en m/s
d_x = datos_de_entrada["coef de difusion x"] # coeficientes de difusión
d_y = datos_de_entrada["coef de difusion y"] # coeficientes de difusión
k = datos_de_entrada["coef de degradacion"] # coef de degradacion
a=datos_de_entrada["ubicacion del vertimiento en x"] #punto de vertimiento en el arreglo
b=datos_de_entrada["ubicacion del vertimiento en y"] #punto de vertimiento en el arreglo
#Amplitud del arreglo
Lx, Ly = datos_de_entrada["amplitud x"],datos_de_entrada["amplitud y"]
    
#creacion de la matriz
m = np.zeros((Lx,Ly))
m[a,b] = (q*concen_vertimiento/(dx*dy))*dt #Esto representa
    #la cantidad en g que pasa en un área (m2) en un tiempo de 1 seg: 300g/m2*s
m[a,b]

def actualizar_conce(m):
    for i in range(1,Lx-1): #si empiezo del 0, dará error por que en el modelo hay un i-1, lo cual saldría -1
        for j in range (1,Ly-1):# los mismo para el Ly-1, no puedo poner 50, por que hay un i+1 y saldria 51 
            adv_x = -ux * (m[i, j] - m[i-1, j]) / dx
            adv_y = -uy * (m[i, j] - m[i, j-1]) / dy
            diff_x = d_x * (m[i+1, j] - 2*m[i, j] + m[i-1, j]) / dx**2
            diff_y = d_y * (m[i, j+1] - 2*m[i, j] + m[i, j-1]) / dy**2
            m[i, j] = m[i, j] + dt * (adv_x + adv_y + diff_x + diff_y-k*m[i,j])
    m[a,b] = m[a,b] + (q*concen_vertimiento/(dx*dy))*dt
    return (m)

for i in range(100):
    actualizar_conce(m)
m

#El bucle es necesario para para que el proceso tienda a la estacionariedad
# Cada valor del arreglo está en masa g, pero es equivalente a mg/L ya que se asume que esta disperso en un
# m3

#Trabajamos en el nv de arcpy
arcpy.env.overwriteOutput=True
gdb = r"C:\Users\brian\OneDrive\Documentos\ArcGIS\Projects\Practica_py\Practica_py.gdb"
arcpy.env.workspace=gdb

#Creamos el feature class
def plotear_punto_vertimiento (nombre):
    with arcpy.EnvManager(outputCoordinateSystem='PROJCS["WGS_1984_UTM_Zone_18S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",-75.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'):
        arcpy.management.CreateFeatureclass(gdb,f"{nombre}" , "POINT", None, "DISABLED", "DISABLED", 'PROJCS["WGS_1984_UTM_Zone_18S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",-75.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]];-5120900 1900 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision', '', 0, 0, 0, '')
    return(gdb + "\\"+ nombre)

#guardamos la ruta del feature class
zona_vertimiento = plotear_punto_vertimiento(nombre ="zona_vertimiento")
zona_vertimiento

#Añadimos el campo de concentracion 
arcpy.management.AddField(zona_vertimiento, "concen", "DOUBLE")
#Coordenadas referenciales del arreglo UTM
x0 = 340642
y0 = 8724956 
#Insertamos los valores del arreglo
with arcpy.da.InsertCursor(zona_vertimiento, ["SHAPE@XY", "concen"]) as cursor:
    for i in range(Lx):
        for j in range(Ly):
            x, y = x0 + i * dx, y0 + j * dy
            cursor.insertRow([(x, y), m[i, j]])
print("Datos exportados a ArcGIS Pro correctamente.")

#Interpolación

with arcpy.EnvManager(outputCoordinateSystem='PROJCS["WGS_1984_UTM_Zone_18S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",-75.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'):
    arcpy.ddd.Idw("zona_vertimiento", "concen", r"C:\Users\brian\OneDrive\Documentos\ArcGIS\Projects\Practica_py\Practica_py.gdb\zona_mezcla_interpolada", 0.1, 6, "VARIABLE 12", None)
    idw_output = r"C:\Users\brian\OneDrive\Documentos\ArcGIS\Projects\Practica_py\Practica_py.gdb\zona_mezcla_interpolada"
    raster = arcpy.Raster(idw_output)

# Calcular estadísticas para asegurarnos que los valores estén disponibles
minimo = raster.minimum
maximo = raster.maximum
minimo
maximo

# Definir parámetros de la clasificación
n = 11 #posiciones
clases = 10  # Número total de clases
primer_rango = 5   # Primer rango fijo (0 a 5)

# Calcular la razón geométrica r
r = (maximo / primer_rango) ** (1 / (n-2))

# Construir la expresión de reclasificación
reclasificacion = f"0 {primer_rango} {primer_rango:.0f};"  # Primer rango fijo
lower_bound = primer_rango

for i in range(9):  # añadimos Desde la segunda clase
    upper_bound = lower_bound * r
    reclasificacion += f"{lower_bound} {upper_bound} {upper_bound:.0f};"
    lower_bound = upper_bound

# Quitar el último punto y coma
reclasificacion = reclasificacion.rstrip(";")
reclasificacion

ruta_salida = r"C:\Users\brian\OneDrive\Documentos\ArcGIS\Projects\Practica_py\Practica_py.gdb\Reclass_zona_de_mezcla7"
arcpy.ddd.Reclassify("zona_mezcla_interpolada", "VALUE", reclasificacion, ruta_salida, "DATA")

#Creamos poligono
arcpy.conversion.RasterToPolygon("Reclass_zona_de_mezcla7", r"C:\Users\brian\OneDrive\Documentos\ArcGIS\Projects\Practica_py\Practica_py.gdb\zdm_poligono1", "SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
poligono = r"C:\Users\brian\OneDrive\Documentos\ArcGIS\Projects\Practica_py\Practica_py.gdb\zdm_poligono1"
# Crear una capa temporal para seleccionar los registros
arcpy.MakeFeatureLayer_management(poligono, "temp_layer")
# Seleccionar los polígonos con gridcode = 5
arcpy.SelectLayerByAttribute_management("temp_layer", "NEW_SELECTION", "gridcode = 5")
# Eliminar los polígonos seleccionados
arcpy.DeleteFeatures_management("temp_layer")
print("Polígonos con gridcode = 5 eliminados correctamente.")
arcpy.cartography.SmoothPolygon("zdm_poligono1", r"C:\Users\brian\OneDrive\Documentos\ArcGIS\Projects\Practica_py\Practica_py.gdb\zdm_poligono_suavizado", "PAEK", "10 Meters", "FIXED_ENDPOINT", "NO_CHECK", None)

#Determina la longitud máxima de la ZdM
#Plotear curva en dicha longitud



#Hagamos un ejercicio, crear un arreglo de 4x4 en el que se actualice
#empezar con valores de 0,1.. hasta el 10.
#arreglo = np.zeros((5,5))
#def actualizacion (arreglo):
    #for i in range(5):
        #for j in range(5):
            #arreglo[i,j]=arreglo[i,j]+1
    #return(arreglo)
#arreglo1 = actualizacion(arreglo)
#arreglo1
#for x in range(5):
    #actualizacion(arreglo)
