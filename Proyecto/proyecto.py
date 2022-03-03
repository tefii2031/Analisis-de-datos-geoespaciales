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

cantones_url = 'https://raw.githubusercontent.com/tefii2031/Analisis-de-datos-geoespaciales/master/datos/cantones.geojson'
redvial_url = 'https://raw.githubusercontent.com/tefii2031/Analisis-de-datos-geoespaciales/master/datos/redvial.geojson'
redvial_por_canton_url = 'datos/redvial_por_canton.geojson'

# Cargar el GeoJason en un dataframe de pandas
pandas_file = gpad.read_file(redvial_por_canton_url)

#
# Sidebar con filtro de categoria
#
lista_categorias = pandas_file.categoria.unique().tolist()
lista_categorias.sort()
filtro_categoria = st.sidebar.selectbox('Seleccione la categoría de red vial', lista_categorias)


#Tabla de pandas con las columnas específicas
pandas_file[['canton', 'area','longitud','densidad','long_autopistas','long_pavimento_1v','long_pavimento_2v','long_sin_pavimento_2v','long_tierra']]
st.dataframe(pandas_file[['canton', 'densidad', 'long_autopistas','long_pavimento_1v','long_pavimento_2v','long_sin_pavimento_2v','long_tierra']])

"""
## Gráfico plotly de barras
"""

#Extraer las 15 cantones de mayor longitud total de red vial
# Dataframe filtrado para usar en graficación
longitud_grafico = pandas_file[['canton', 'longitud','long_autopistas','long_pavimento_1v','long_pavimento_2v','long_sin_pavimento_2v','long_tierra']].sort_values("longitud", ascending=[False]).head(15)
#Gráfico plotly de barras apiladas 
fig = px.bar(longitud_grafico, x="canton", y=['long_autopistas','long_pavimento_1v','long_pavimento_2v','long_sin_pavimento_2v','long_tierra'], title="Cantones de mayor longitud total de red vial")
fig.show()

"""
##Gráfico plotly de pastel 

Porcentaje de red vial de los 15 cantones de mayor longitud total de la red vial, con respecto a la longitud de la red vial en todo el país.
La porción (slice) adicional en el gráfico de pastel llamada “Otros cantones”, correspondiente al porcentaje de la suma de la red vial en los 67 cantones restantes."
"""

#ordenar los valores por longitud
pastel = pandas_file[['canton', 'longitud']].sort_values("longitud", ascending=[False])
#reset al index
pastel = pastel.reset_index()
#extraer la longitud de valor 15
longitud_15= pastel['longitud'].loc[14]
#cambiar el canton a los siguientes valores luego del 15
pastel.loc[pastel['longitud'] < longitud_15 , 'canton'] = 'Otros cantones' 
#Gráfico plotly de pastel 
fig = px.pie(pastel, values='longitud', names='canton', title='Porcentaje de los 15 cantones de mayor longitud total de la red vial en el país')
fig.show()

"""
## Mapa folium 
Un mapa folium con las siguientes capas:
* Capa base (OpenStreetMap, Stamen, etc.).
* Capa de coropletas correspondiente a la densidad de la red vial en los cantones.
* Líneas de la red vial.

Y los siguientes controles:
* Control para activar y desactivar capas.
* Escala

"""

# Cargar el GeoJason en un dataframe de pandas
densidad_file = gpad.read_file(redvial_por_canton_url)
# Cargar el GeoJason en un dataframe de pandas
cantones_file = gpad.read_file(cantones_url)

# Creación del mapa base
mapa= folium.Map(
    location=[9.8, -84], 
    width=1000, height=1000, 
    zoom_start=8,
    control_scale=True,
    tiles='Stamen Watercolor'
    )


#Añadir mapa de coropletas
folium.Choropleth(
    name="Densidad de la red vial en los cantones de Costa Rica",
    geo_data=cantones_file,
    data=densidad_file,
    columns=['id', 'densidad'],
    bins=8,
    key_on='feature.properties.id',
    fill_color='Reds', 
    fill_opacity=0.5, 
    line_opacity=1,
    legend_name='densidad',
    smooth_factor=0 ).add_to(mapa)

#añadir capa con las lineas de red vial
folium.GeoJson(data=redvial_url, name='Red vial').add_to(mapa)

# Control de capas
folium.LayerControl().add_to(mapa)

# Despliegue del mapa
mapa