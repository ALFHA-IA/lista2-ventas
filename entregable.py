import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import calendar
import streamlit as st

# Título de la aplicación
st.title('Dashboard de Frecuencia de Compra')

# --- 1. PREPARACIÓN DE DATOS ---

# Leer CSV
archivo = 'Lista_Ventas_Detalle-_2_.csv'
columnas = [
    'fecha', 'documento', 'nro_doc', 'cont_cred', 'medio_pago',
    'doc_cliente', 'cliente', 'telefono', 'observacion', 'moneda',
    'articulos', 'dato_extra', 'cantidad', 'importe', 'tc',
    'importe_soles', 'vendedor'
]

try:
    df = pd.read_csv(archivo, skiprows=2, names=columnas)
except FileNotFoundError:
    st.error(f"Error: El archivo '{archivo}' no fue encontrado.")
    st.stop()

# Limpieza
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df['importe_soles'] = pd.to_numeric(df['importe_soles'], errors='coerce')
df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
df = df.dropna(subset=['fecha', 'importe_soles', 'cantidad'])

# Rango de fechas desde julio del año pasado hasta hoy
hoy = pd.Timestamp.today()
inicio = pd.Timestamp(year=(hoy - pd.DateOffset(years=1)).year, month=7, day=1)
df = df[df['fecha'] >= inicio]

# Crear columna de mes y año legible y ordenada
df['mes_orden'] = pd.to_datetime(df['fecha'].dt.to_period('M').astype(str))
df['mes_nombre'] = df['fecha'].dt.month.apply(lambda x: calendar.month_name[x]) + ' ' + df['fecha'].dt.year.astype(str)

# Agrupar por producto y mes
frecuencia = df.groupby(['articulos', 'mes_nombre', 'mes_orden']).size().reset_index(name='frecuencia')
frecuencia = frecuencia.sort_values('mes_orden')

# --- 2. GENERACIÓN DEL GRÁFICO ---

# Top 30 productos
top_productos = frecuencia.groupby('articulos')['frecuencia'].sum().sort_values(ascending=False).head(30).index
frecuencia_top = frecuencia[frecuencia['articulos'].isin(top_productos)]

# Crear la figura (con los botones dropdown)
fig = go.Figure()

# Trazas ocultas al inicio
for producto in top_productos:
    data_producto = frecuencia_top[frecuencia_top['articulos'] == producto]
    fig.add_trace(go.Bar(
        x=data_producto['mes_nombre'],
        y=data_producto['frecuencia'],
        name=producto,
        visible=False
    ))

# Mostrar solo el primero por defecto
if len(fig.data) > 0:
    fig.data[0].visible = True

# Botones dropdown
botones = []
for i, producto in enumerate(top_productos):
    visibilidad = [False] * len(top_productos)
    visibilidad[i] = True
    botones.append(dict(
        label=producto,
        method='update',
        args=[{'visible': visibilidad},
              {'title': f'Frecuencia de Compra: {producto}'}]
    ))

# Layout
if len(botones) > 0:
    fig.update_layout(
        updatemenus=[{
            'active': 0,
            'buttons': botones,
            'x': 1.15,
            'xanchor': 'left',
            'y': 1,
            'yanchor': 'top'
        }],
        title=f'Frecuencia de Compra: {top_productos[0]}',
        xaxis_title='Mes',
        yaxis_title='Frecuencia de Compra',
        width=1300,
        height=600,
        xaxis_tickangle=-45
    )
else:
    st.warning("No se encontraron suficientes datos para los productos principales.")
    st.stop()


# --- 3. MOSTRAR EL GRÁFICO CON STREAMLIT ---
st.plotly_chart(fig, use_container_width=True)