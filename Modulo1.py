#Modulo1
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import arcpy
#Para una primera etapa asumimremos valores
def insertar_datos (datos_de_entrada):
    """ 
    Desempaca y define variables iniciales, creando un arreglo inicial
    y definiendo un punto de vertimiento dentro del mismo

    Parametros:
        parametros (dict): Diccionario con los siguientes keys:
            dx, dy (float): Tamaño de celda (m)
            dt (float): Paso de tiempo (s)
            q (float): Caudal (m³/s)
            concen_vertimiento (float): Concentración (mg/L)
            ux, uy (float): Velocidad del flujo en el cuerpo de agua(m/s)
            d_x, d_y (float): Coeficientes de difusión
            k (float): Coeficiente de degradación (1/s)
            Lx, Ly (int): Dimensiones de la matriz
            a, b (int): Posición del vertimiento (opcional, default: 20, 100)
    Returns:
        m (array): matriz_inicial
        Variables globales definidas
    """   
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
    c=datos_de_entrada["ubicacion del vertimiento 1 en x"] #punto de vertimiento 1 en el arreglo
    d=datos_de_entrada["ubicacion del vertimiento 1 en y"] #punto de vertimiento 1 en el arreglo
    #Amplitud del arreglo
    Lx, Ly = datos_de_entrada["amplitud x"],datos_de_entrada["amplitud y"]
    #creacion de la matriz
    m = np.zeros((Lx,Ly))
    m[a,b] = (q*concen_vertimiento/(dx*dy))*dt #Esto representa
    #la cantidad en g que pasa en un área (m2) en un tiempo de 1 seg: 300g/m2*s
    m[c,d] = (q*concen_vertimiento/(dx*dy))*dt
    return dx,dy,dt,q,concen_vertimiento,ux,uy,d_x,d_y,k,a,b,c,d,Lx,Ly,m,m[a,b],m[c,d]

def actualizar_conce(dx,dy,dt,q,concen_vertimiento,ux,uy,d_x,d_y,k,a,b,c,d,Lx,Ly,m):    
    """ 
    Modela la dispersion del contaminante, actualizando el arreglo hasta converger a la
    estacionariedad mediante 100 iteraciones. 
    - Utiliza la ecuación diferencial de advección y dispersión, cuya resolución se realizó
      con un método de diferncias finitas.
    - Considera un vertimiento continuo en el tiempo

    Parámetros:
        parámetros previamente establecidos(dx,dy,dt,
        q,concen_vertimiento,ux,uy,d_x,d_y,k,a,b,Lx,Ly)
    
    Return
        m (array): arreglo actualizado hasta i-esima iteración
    """
    for i in range(1,Lx-1): #si empiezo del 0, dará error por que en el modelo hay un i-1, lo cual saldría -1
        for j in range (1,Ly-1):# los mismo para el Ly-1, no puedo poner 50, por que hay un i+1 y saldria 51 
            adv_x = -ux * (m[i, j] - m[i-1, j]) / dx
            adv_y = -uy * (m[i, j] - m[i, j-1]) / dy
            diff_x = d_x * (m[i+1, j] - 2*m[i, j] + m[i-1, j]) / dx**2
            diff_y = d_y * (m[i, j+1] - 2*m[i, j] + m[i, j-1]) / dy**2
            m[i, j] = m[i, j] + dt * (adv_x + adv_y + diff_x + diff_y-k*m[i,j])
    m[a,b] = m[a,b] + (q*concen_vertimiento/(dx*dy))*dt
    m[c,d] = m[c,d] + (q*concen_vertimiento/(dx*dy))*dt
    return (m)