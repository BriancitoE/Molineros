import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import arcpy
def interpolacion (nombre,gdb,nombre_salida):
    """ 
    Genera un raster que representa la interpolacion de los puntos

    Parámetros:
        nombre (string): nombre del feature class previamente creado
        gdb (string): ruta del geodatabase creado en nuestro arcgis
        nombre_salida: nombre del raster 
    
    return:
        ruta del raster interpolado (string)
    """
    with arcpy.EnvManager(outputCoordinateSystem='PROJCS["WGS_1984_UTM_Zone_18S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",-75.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'):
        arcpy.ddd.Idw(nombre, "concen", gdb + "\\"+ nombre_salida, 0.1, 6, "VARIABLE 12", None)
        idw_output = gdb + "\\"+ nombre_salida
        raster = arcpy.Raster(idw_output)
        return raster

def reclass (raster,clases,Eca):
    """ 
    crea un rango de clasificaciones cuyos limites son enteros
    y siguen una distribución exponencial

    parámetros:
        raster (string): ruta del raster creado
        clases (int): numero de clases
        Eca (int): estándar de calidad ambiental para un contaminante determinado
    
    return:
        rango de clasificaciones  
    
    """
    minimo = raster.minimum
    maximo = raster.maximum
   
    # Definir parámetros de la clasificación
    # Número total de clases
    n = clases+1 
    primer_rango = Eca   # Primer rango fijo (0 a 5)

    # Calcular la razón geométrica r
    r = (maximo / primer_rango) ** (1 / (n-2))

    # Construir la expresión de reclasificación
    reclasificacion = f"0 {primer_rango} {primer_rango:.0f};"  # Primer rango fijo
    lower_bound = primer_rango

    for i in range(clases-1):  # añadimos Desde la segunda clase
        upper_bound = lower_bound * r
        reclasificacion += f"{lower_bound} {upper_bound} {upper_bound:.0f};"
        lower_bound = upper_bound

    # Quitar el último punto y coma
    reclasificacion = reclasificacion.rstrip(";")
    return reclasificacion

def reclassify (nombre,reclasificacion,gdb, nombre_salida):
    """
    Aplica la reclasificacion con distribucion exponencial al raster
    previamente creada
    
    Parámetros:
        nombre (string): nombre del raster previamente creado
        reclasificacion (list): rango de clasificaciones
        gdb (string): ruta del geodatabase creado en nuestro arcgis
        nombre_salida (string): nombre del raster interpolado y reclasificado
    
    return:
        ruta del raster interpolado y reclasificado
    """
    arcpy.ddd.Reclassify(nombre, "VALUE", reclasificacion, gdb + "\\"+ nombre_salida, "DATA")