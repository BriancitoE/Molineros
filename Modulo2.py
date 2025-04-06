import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import arcpy


#Creamos el feature class
def feature_class (nombre,gdb):
    """ 
    Crea un feature class (pountos) en la zona 18S
    
    Parámetros:
        nombre (string): del feature class que vamos a crear
        gdb (string):ruta del geodatabase creado en nuestro arcgis
    
    Return:
        ruta del feature class (string)
    """
    with arcpy.EnvManager(outputCoordinateSystem='PROJCS["WGS_1984_UTM_Zone_18S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",-75.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'):
        arcpy.management.CreateFeatureclass(gdb,f"{nombre}" , "POINT", None, "DISABLED", "DISABLED", 'PROJCS["WGS_1984_UTM_Zone_18S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",-75.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]];-5120900 1900 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision', '', 0, 0, 0, '')
    return(gdb + "\\"+ nombre)

#Añadimos el campo de concentracion 
def plotear_arreglo (zona_vertimiento,x0,y0,Lx,Ly,dx,dy,m):
    """ 
    Inserta el campo [Concentracion] y  los valores
    del arreglo m en el feature class

    Parámetros
        zona_vertimiento: ruta del feature class
        x0 (float): coordenada utm x del vertimiento
        y0 (float): coordenada utm y del vertimiento
        Lx (int): rango del arreglo en x
        Ly (int): rango del arreglo en y
        dx, dy (float): Tamaño de celda (m): 
        m (array): arreglo actualizado hasta i-esima iteración
    
    return
        ruta del feature class  (string)
    """
    arcpy.management.AddField(zona_vertimiento, "concen", "DOUBLE")

    with arcpy.da.InsertCursor(zona_vertimiento, ["SHAPE@XY", "concen"]) as cursor:
        for i in range(Lx):
            for j in range(Ly):
                x, y = x0 + i * dx, y0 + j * dy
                cursor.insertRow([(x, y), m[i, j]])
    print("Datos exportados a ArcGIS Pro correctamente.")