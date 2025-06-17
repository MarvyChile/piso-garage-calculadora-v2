import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="centered")
st.title("Piso Garage - Calculadora V2")

# 1. Unidad y dimensiones
unidad = st.selectbox("Selecciona la unidad de medida", ["metros", "centímetros"])
factor = 1 if unidad == "metros" else 0.01
min_val = 1.0 if unidad == "metros" else 10.0

ancho_input = st.number_input(f"Ancho del espacio ({unidad})", min_value=min_val, value=4.0 if unidad == "metros" else 400.0, step=1.0)
largo_input = st.number_input(f"Largo del espacio ({unidad})", min_value=min_val, value=6.0 if unidad == "metros" else 600.0, step=1.0)

ancho_m = ancho_input * factor
largo_m = largo_input * factor
st.markdown(f"**Área total:** {round(ancho_m * largo_m, 2)} m²")

# 2. Bordillos y esquineros
incluir_bordillos = st.checkbox("Agregar bordillos", value=True)
incluir_esquineros = st.checkbox("Agregar esquineros", value=True)
pos_bord = st.multiselect("¿Dónde colocar bordillos?", ["Arriba", "Abajo", "Izquierda", "Derecha"], default=["Arriba", "Abajo", "Izquierda", "Derecha"])

# 3. Colores
colores = {
    "Blanco":"#FFFFFF", "Negro":"#000000", "Gris":"#B0B0B0", "Gris Oscuro":"#4F4F4F",
    "Azul":"#0070C0", "Celeste":"#00B0F0", "Amarillo":"#FFFF00", "Verde":"#00B050", "Rojo":"#FF0000"
}
lista_colores = list(colores.keys())
color_base = st.selectbox("Color base", lista_colores, index=lista_colores.index("Gris"))
color_secundario = st.selectbox("Color secundario", lista_colores, index=lista_colores.index("Rojo"))

# 4. Calcular grilla
cols = math.ceil(ancho_m / 0.4)
rows = math.ceil(largo_m / 0.4)

if "df" not in st.session_state or st.session_state.df.shape != (rows, cols):
    st.session_state.df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

# 5. Generar patrón decorativo
def generar_diseno_decorativo():
    df = pd.DataFrame([[color_base]*cols for _ in range(rows)])
    margen = max(1, min(rows, cols) // 5)  # Asegura al menos 1

    for y in range(margen, rows - margen):
        for x in range(margen, cols - margen):
            if x in (margen, cols - margen - 1) or y in (margen, rows - margen - 1):
                df.iat[y, x] = color_secundario

    st.session_state.df = df

if st.button("Generar diseño aleatorio"):
    generar_diseno_decorativo()

# 6. Calcular cantidades
total_palmetas = rows * cols
total_bordillos = 0
if incluir_bordillos:
    if "Arriba" in pos_bord: total_bordillos += cols
    if "Abajo" in pos_bord: total_bordillos += cols
    if "Izquierda" in pos_bord: total_bordillos += rows
    if "Derecha" in pos_bord: total_bordillos += rows
total_esquineros = 4 if incluir_esquineros else 0

# Contar colores usados
conteo_colores = st.session_state.df.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).to_dict()

# 7. Mostrar cantidades
st.markdown("### Cantidad necesaria:")
for color, count in conteo_colores.items():
    st.markdown(f"- **{color}:** {count} palmetas")
st.markdown(f"- **Bordillos:** {total_bordillos}")
st.markdown(f"- **Esquineros:** {total_esquineros}")

# 8. Dibujar
df = st.session_state.df
borde_general = "#FFFFFF" if color_base == "Negro" else "#000000"
color_bordillo = "#000000"

fig, ax = plt.subplots(figsize=(cols/2, rows/2))
for y in range(rows):
    for x in range(cols):
        color = colores.get(df.iat[y, x], "#FFFFFF")
        ax.add_patch(plt.Rectangle((x, rows-1-y), 1, 1, facecolor=color, edgecolor=borde_general, linewidth=0.8))

# Bordillos
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

# Esquineros
if incluir_esquineros:
    s = 0.15
    for (cx, cy) in [(0,0), (0,rows), (cols,0), (cols,rows)]:
        ax.add_patch(plt.Rectangle((cx-s/2, cy-s/2), s, s, facecolor=color_bordillo, edgecolor=borde_general, linewidth=0.8))

# Medidas reales
largo_real = rows * 0.4
ancho_real = cols * 0.4
if incluir_bordillos:
    if "Arriba" in pos_bord: largo_real += 0.06
    if "Abajo" in pos_bord: largo_real += 0.06
    if "Izquierda" in pos_bord: ancho_real += 0.06
    if "Derecha" in pos_bord: ancho_real += 0.06

# Mostrar medidas
ax.text(cols/2, rows + 0.6, f"{ancho_real:.2f} m", ha='center', va='bottom', fontsize=10)
ax.text(cols + 0.6, rows/2, f"{largo_real:.2f} m", ha='left', va='center', rotation=90, fontsize=10)
ax.plot([0, cols], [rows + 0.5, rows + 0.5], color="#666666", lw=0.8)
ax.plot([cols + 0.5, cols + 0.5], [0, rows], color="#666666", lw=0.8)

# Finalizar
ax.set_xlim(-0.5, cols + 1.5)
ax.set_ylim(-0.5, rows + 1.5)
ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)
