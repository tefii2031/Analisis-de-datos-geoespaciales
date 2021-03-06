"""Tarea 3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/161YdXmre5OWCn3D7Ik8Qqxcs55R8PQUG

#Tarea 03 - Análisis de datos geoespaciales mediante pandas, plotly, geopandas y folium

## Estudiantes:

Daniel Salazar Mora - B87214
Stephanie María Leitón Ramírez - B74106

##Importando las bibliotecas
"""

import os
import requests
import zipfile
import csv
from functools import partial
from shapely.geometry import Point, mapping, shape
from shapely.ops import transform
from owslib.wfs import WebFeatureService
from geojson import dump
import fiona
import fiona.crs
import math
import folium
import geopandas as gpad
import pandas as pd
import contextily as cx
import matplotlib.pyplot as plt
# %matplotlib inline
import plotly.express as px
from folium import Marker
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
import streamlit as st

#
# Configuración de la página
#
st.set_page_config(layout='wide')


"""
## Obtención de datos
Se usan las capas de Web Feature Service (WFS) publicadas por el Instituto Geográfico Nacional (IGN) en el Sistema Nacional de Información Territorial (SNIT):

Límite cantonal 1:5000
https://www.snitcr.go.cr/ico_servicios_ogc_info?k=bm9kbzo6MjY=&nombre=IGN%20Cartograf%C3%ADa%201:5mil
 
Red vial 1:200000
https://www.snitcr.go.cr/ico_servicios_ogc_info?k=bm9kbzo6NDI=&nombre=IGN%201:200mil

"""
#
# URL de archivos a utilizar
#
cantones_url = 'https://raw.githubusercontent.com/tefii2031/Analisis-de-datos-geoespaciales/master/datos/cantones.geojson'
redvial_url = 'https://raw.githubusercontent.com/tefii2031/Analisis-de-datos-geoespaciales/master/datos/redvial.geojson'
redvial_por_canton_url = 'datos/redvial_por_canton.geojson'

# Cargar el GeoJason en un dataframe de pandas
redvial_file = gpad.read_file(redvial_url)
#redvial_file = redvial_file.to_crs(4326)

cantones_file = gpad.read_file(cantones_url)
#cantones_file = cantones_file.to_crs(4326)

#pandas_file
#
# Sidebar con filtro de categoria
#
lista_categorias = redvial_file.categoria.unique().tolist()
lista_categorias.sort()
filtro_categoria = st.sidebar.selectbox('Seleccione la categoría de red vial', lista_categorias)

""" 
## Tabla de cantones

Muestra:
1. El nombre del cantón.
2. La longitud de las vías de la categoría seleccionada en la barra lateral.
3. La densidad de la red vial del cantón para esa categoría.
"""

# TODO agregar columna de categoria en el file
# Filtrado
redvial_file_filtrado = redvial_file[redvial_file['categoria'] == filtro_categoria]

# "Join" espacial de las capas de Cantones y Redes Viales
redvial_por_canton = cantones_file.overlay(redvial_file_filtrado, how="intersection", keep_geom_type=False)
panda = redvial_por_canton.groupby("canton").agg(
                            longitud = ("longitud","sum")
                            )
panda = panda.reset_index() # para convertir la serie a dataframe
panda
