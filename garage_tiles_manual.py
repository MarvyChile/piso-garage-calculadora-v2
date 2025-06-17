import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="centered")
st.title("Piso Garage - Calculadora V1")

# 1. Unidad de medida y entradas
unidad = st.selectbox("Selecciona la unidad de medida", ["metros", "centímetros"], key="unidad")
factor = 1 if unidad == "metros" else 0.01
min_val = 1.0 if unidad == "metros" else 10.0

ancho_input = st.number_input(
    f"Ancho del espacio ({unidad})", min_value=min_val,
    value=4.0 if unidad == "metros" else 400.0, step=1.0, key="ancho")
largo_input = st.number_input(
    f"Largo del espacio ({unidad})", min_value=min_val,
    value=6.0 if unidad == "metros" else 600.0, step=1.0, key="largo")

ancho_m = ancho_input * factor
largo_m = largo_input * factor
area_m2 = round(ancho_m * largo_m, 2)
st.markdown(f"**Área total:** {area_m2} m²")

# 2. Bordillos y esquineros
incluir_bordillos = st.checkbox("Agregar bordillos", value=True)
incluir_esquineros = st.checkbox("Agregar esquineros", value=True)
pos_bord = st.multiselect(
    "¿Dónde colocar bordillos?", ["Arriba", "Abajo", "Izquierda", "Derecha"],
    default=["Arriba", "Abajo", "Izquierda", "Derecha"]
)

# 3. Colores y color base
colores = {
    "Blanco":"#FFFFFF","Negro":"#000000","Gris":"#B0B0B0","Gris Oscuro":"#4F4F4F",
    "Azul":"#0070C0","Celeste":"#00B0F0","Amarillo":"#FFFF00","Verde":"#00B050","Rojo":"#FF0000"
}
lista_colores = list(colores.keys())
color_base = st.selectbox("Color base", lista_colores, index=lista_colores.index("Blanco"))

# 4. Cálculo de grilla
cols = math.ceil(ancho_m / 0.4)
rows = math.ceil(largo_m / 0.4)

# 5. Inicializar y actualizar DataFrame
if 'df' not in st.session_state or st.session_state.df.shape != (rows, cols):
    st.session_state.df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

if st.button("Aplicar color base"):
    st.session_state.df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

# 6. Calcular piezas necesarias
total_palmetas = rows * cols
total_bordillos = 0
total_esquineros = 0
if incluir_bordillos:
    if "Arriba" in pos_bord:
        total_bordillos += cols
    if "Abajo" in pos_bord:
        total_bordillos += cols
    if "Izquierda" in pos_bord:
        total_bordillos += rows
    if "Derecha" in pos_bord:
        total_bordillos += rows
if incluir_esquineros:
    total_esquineros = 4

# 7. Mostrar cantidad necesaria
st.markdown(f"""
### Cantidad necesaria:
- **Palmetas:** {total_palmetas}
- **Bordillos:** {total_bordillos}
- **Esquineros:** {total_esquineros}
""")

# 8. Preparar visualización
df = st.session_state.df
borde_general = "#FFFFFF" if color_base == "Negro" else "#000000"
color_bordillo = "#000000"

fig, ax = plt.subplots(figsize=(cols/2, rows/2))
for y in range(rows):
    for x in range(cols):
        color_hex = colores.get(df.iat[y, x], "#FFFFFF")
        ax.add_patch(plt.Rectangle(
            (x, rows-1-y), 1, 1,
            facecolor=color_hex,
            edgecolor=borde_general,
            linewidth=0.8
        ))

# 9. Bordillos
if incluir_bordillos:
    for side in pos_bord:
        if side == "Arriba":
            for x in range(cols):
                ax.add_patch(plt.Rectangle((x, rows), 1, 0.15, facecolor=color_bordillo, edgecolor=borde_general, linewidth=0.8))
        if side == "Abajo":
            for x in range(cols):
                ax.add_patch(plt.Rectangle((x, -0.15), 1, 0.15, facecolor=color_bordillo, edgecolor=borde_general, linewidth=0.8))
        if side == "Izquierda":
            for y in range(rows):
                ax.add_patch(plt.Rectangle((-0.15, y), 0.15, 1, facecolor=color_bordillo, edgecolor=borde_general, linewidth=0.8))
        if side == "Derecha":
            for y in range(rows):
                ax.add_patch(plt.Rectangle((cols, y), 0.15, 1, facecolor=color_bordillo, edgecolor=borde_general, linewidth=0.8))

# 10. Esquineros
if incluir_esquineros:
    s = 0.15
    for (cx, cy) in [(0,0), (0,rows), (cols,0), (cols,rows)]:
        ax.add_patch(plt.Rectangle((cx-s/2, cy-s/2), s, s, facecolor=color_bordillo, edgecolor=borde_general, linewidth=0.8))

# 11. Calcular medidas reales
longitud_real_m = cols * 0.4
ancho_real_m = rows * 0.4

if incluir_bordillos:
    if "Izquierda" in pos_bord:
        longitud_real_m += 0.06
    if "Derecha" in pos_bord:
        longitud_real_m += 0.06
    if "Arriba" in pos_bord:
        ancho_real_m += 0.06
    if "Abajo" in pos_bord:
        ancho_real_m += 0.06

# 12. Medidas visuales ajustadas
ax.text(cols/2, rows + 0.6, f"{longitud_real_m:.2f} m", ha='center', va='bottom', fontsize=10)
ax.plot([0, 0], [rows + 0.3, rows + 0.5], color="#666666", lw=0.8)
ax.plot([cols, cols], [rows + 0.3, rows + 0.5], color="#666666", lw=0.8)
ax.plot([0, cols], [rows + 0.5, rows + 0.5], color="#666666", lw=0.8)

ax.text(cols + 0.6, rows/2, f"{ancho_real_m:.2f} m", ha='left', va='center', rotation=90, fontsize=10)
ax.plot([cols + 0.3, cols + 0.5], [0, 0], color="#666666", lw=0.8)
ax.plot([cols + 0.3, cols + 0.5], [rows, rows], color="#666666", lw=0.8)
ax.plot([cols + 0.5, cols + 0.5], [0, rows], color="#666666", lw=0.8)

# 13. Finalización
ax.set_xlim(-0.5, cols + 1.5)
ax.set_ylim(-0.5, rows + 1.5)
ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)
