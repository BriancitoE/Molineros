#Modulo test
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import arcpy
import Modulo1
import Modulo2
import Modulo3
import Modulo4

#El objetivo de este código y definir la extensión de la zona de mezcla
#´de un vertimiento en un cuerpo de agua léntico.

#1. Definimos variables, parámetros y creamos el arreglo con el punto del vertimiento
datos = {"tamaño de celda x":1, 
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
        "ubicacion del vertimiento en y":100,
        "ubicacion del vertimiento 1 en x":50,
        "ubicacion del vertimiento 1 en y":50}
dx,dy,dt,q,concen_vertimiento,ux,uy,d_x,d_y,k,a,b,c,d,Lx,Ly,m,m[a,b],m[c,d]=Modulo1.insertar_datos(datos)


#2. Generamos un bucle de 100 corridas para alcanzar la estacionariedad de la dispersion
for i in range(100):
    Modulo1.actualizar_conce(dx,dy,dt,q,concen_vertimiento,ux,uy,d_x,d_y,k,a,b,c,d,Lx,Ly,m)
m


#3 Ploteamos en el AcrgisPro
#Definimos la geodatabase
arcpy.env.overwriteOutput=True
geodatabase = r"C:\Users\brian\OneDrive\Documentos\ArcGIS\Projects\Practica_py\Practica_py.gdb"
arcpy.env.workspace=geodatabase
#Creamos feature class
zona_de_vertimiento = Modulo2.feature_class(nombre ="zona_vertimiento",gdb=geodatabase)
#Ploteamos valores, definiendo un punto de referencia dentro de la Zona 18S 
# y creamos la Zona de mezlcla ZdM
x0 = 340642
y0 = 8724956 
Modulo2.plotear_arreglo(zona_de_vertimiento,x0,y0,Lx,Ly,dx,dy,m)



#4 Interpolamos ZdM
#Creamos la interpolación
raster_ZdM = Modulo3.interpolacion(nombre="zona_vertimiento",gdb=geodatabase,nombre_salida="ZdM_interpolada1")
#Creamos nuevos rangos de clasificacion 
rangos_reclasificion = Modulo3.reclass(raster=raster_ZdM,clases=10,Eca=5)
#Aplicamos la reclasificacion
Modulo3.reclassify(nombre="ZdM_interpolada1",reclasificacion=rangos_reclasificion,gdb=geodatabase,nombre_salida="ZdM_interpol_reclass")



#5 Creamos polígono
Modulo4.polygon(nombre="ZdM_interpol_reclass",gdb=geodatabase,nombre_salida="ZdM_Poligono",Eca=5)
Modulo4.suavizado("ZdM_Poligono",geodatabase,"ZdM_Pol_Suavizado")
