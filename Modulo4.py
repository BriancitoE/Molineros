#Creamos poligono
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import arcpy
def polygon (nombre,gdb,nombre_salida, Eca):
    """ 
    Crea un polígono a partir del raster reclasificado, eliminando
    los valores por debajo del ECA

    Parámetros:
        nombre (string): nombre del raster interpolado y reclasificado
        gdb (string): ruta del geodatabase creado en nuestro arcgis
        nombre_salida (string): nombre del polígono creado
        Eca (string): estándar de calidad ambiental para un contaminante determinado
    return:
        ruta del polígono creado 
    """
    arcpy.conversion.RasterToPolygon(nombre, gdb + "\\"+ nombre_salida, "SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
    poligono = gdb + "\\"+ nombre_salida
    # Crear una capa temporal para seleccionar los registros
    arcpy.MakeFeatureLayer_management(poligono, "temp_layer")
    # Seleccionar los polígonos con gridcode = 5
    arcpy.SelectLayerByAttribute_management("temp_layer", "NEW_SELECTION", f"gridcode = {Eca}")
    # Eliminar los polígonos seleccionados
    arcpy.DeleteFeatures_management("temp_layer")
    print("Polígono creado correctamente.")

def suavizado (nombre,gdb,nombre_salida):    
    """
    Suaviza las líneas del polígono creado

    Parámetros:
        nombre (string): nombre del polígono creado previamente
        gdb (string): ruta del geodatabase creado en nuestro arcgis
        nombre_salida (string): nombre del polígono suavizado
    
    Return:
        ruta del polígono suavizado
    """
    arcpy.cartography.SmoothPolygon(nombre, gdb + "\\" + nombre_salida , "PAEK", "10 Meters", "FIXED_ENDPOINT", "NO_CHECK", None)
