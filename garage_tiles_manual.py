
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="centered")
st.title("Piso Garage - Calculadora V2")

unidad = st.selectbox("Selecciona la unidad de medida", ["metros", "centímetros"])
factor = 1 if unidad == "metros" else 0.01
min_val = 1.0 if unidad == "metros" else 10.0

ancho_input = st.number_input("Ancho del espacio", min_value=min_val, value=4.0 if unidad == "metros" else 400.0, step=1.0)
largo_input = st.number_input("Largo del espacio", min_value=min_val, value=6.0 if unidad == "metros" else 600.0, step=1.0)

ancho_m = ancho_input * factor
largo_m = largo_input * factor
st.markdown(f"**Área total:** {round(ancho_m * largo_m, 2)} m²")

incluir_bordillos = st.checkbox("Agregar bordillos", value=True)
incluir_esquineros = st.checkbox("Agregar esquineros", value=True)
pos_bord = st.multiselect("¿Dónde colocar bordillos?", ["Arriba", "Abajo", "Izquierda", "Derecha"], default=["Arriba", "Abajo", "Izquierda", "Derecha"])

colores = {
    "Blanco":"#FFFFFF", "Negro":"#000000", "Gris":"#B0B0B0", "Gris Oscuro":"#4F4F4F",
    "Azul":"#0070C0", "Celeste":"#00B0F0", "Amarillo":"#FFFF00", "Verde":"#00B050", "Rojo":"#FF0000"
}
lista_colores = list(colores.keys())
color_base = st.selectbox("Color base", lista_colores, index=lista_colores.index("Gris"))
color_secundario = st.selectbox("Color secundario", lista_colores, index=lista_colores.index("Rojo"))

cols = math.ceil(ancho_m / 0.4)
rows = math.ceil(largo_m / 0.4)

if "df" not in st.session_state or st.session_state.df.shape != (rows, cols):
    st.session_state.df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

modelo = st.selectbox(
    "Seleccionar modelo de diseño decorativo",
    [
        "MODELO A - Marco exterior",
        "MODELO B - Doble marco",
        "MODELO C - Cuadro central",
        "MODELO D - Patrón tipo ajedrez",
        "MODELO E - Cruces diagonales",
        "MODELO F - Banda central + bordes horizontales",
        "MODELO G - Cruz central completa"
    ]
)

def aplicar_modelo_diseno():
    df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

    if modelo.startswith("MODELO A"):
        margen = max(1, min(rows, cols) // 5)
        for y in range(rows):
            for x in range(cols):
                if (x == margen or x == cols - margen - 1 or y == margen or y == rows - margen - 1):
                    df.iat[y, x] = color_secundario

    elif modelo.startswith("MODELO B"):
        for y in range(rows):
            for x in range(cols):
                if (x in [0, cols-1] or y in [0, rows-1]) or (x in [1, cols-2] or y in [1, rows-2]):
                    df.iat[y, x] = color_secundario

    elif modelo.startswith("MODELO C"):
        mid_x = cols // 2
        mid_y = rows // 2
        for y in range(mid_y - 1, mid_y + 2):
            for x in range(mid_x - 1, mid_x + 2):
                if 0 <= y < rows and 0 <= x < cols:
                    df.iat[y, x] = color_secundario

    elif modelo.startswith("MODELO D"):
        for y in range(rows):
            for x in range(cols):
                if (x + y) % 2 == 0:
                    df.iat[y, x] = color_secundario

    elif modelo.startswith("MODELO E"):
        for y in range(rows):
            for x in range(cols):
                if x == y or x == cols - y - 1:
                    df.iat[y, x] = color_secundario

    elif modelo.startswith("MODELO F"):
        for x in range(cols):
            df.iat[0, x] = color_secundario
            df.iat[rows-1, x] = color_secundario
        for y in range(rows):
            df.iat[y, cols//2] = color_secundario

    elif modelo.startswith("MODELO G"):
        for y in range(rows):
            df.iat[y, cols//2] = color_secundario
        for x in range(cols):
            df.iat[rows//2, x] = color_secundario

    st.session_state.df = df

if st.button("Aplicar diseño decorativo"):
    aplicar_modelo_diseno()

# Cantidades
df = st.session_state.df
total_palmetas = rows * cols
total_bordillos = sum([cols if side in ["Arriba", "Abajo"] else rows for side in pos_bord]) if incluir_bordillos else 0
total_esquineros = 4 if incluir_esquineros else 0

conteo_colores = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).to_dict()

st.markdown("### Cantidad necesaria:")
for color, count in conteo_colores.items():
    st.markdown(f"- **{color}:** {count} palmetas")
st.markdown(f"- **Bordillos:** {total_bordillos}")
st.markdown(f"- **Esquineros:** {total_esquineros}")

# Visualización
borde_general = "#FFFFFF" if color_base == "Negro" else "#000000"
color_bordillo = "#000000"

fig, ax = plt.subplots(figsize=(cols/2, rows/2))
for y in range(rows):
    for x in range(cols):
        c = colores.get(df.iat[y, x], "#FFFFFF")
        ax.add_patch(plt.Rectangle((x, rows-1-y), 1, 1, facecolor=c, edgecolor=borde_general, linewidth=0.8))

if incluir_bordillos:
    for side in pos_bord:
        if side == "Arriba":
            for x in range(cols):
                ax.add_patch(plt.Rectangle((x, rows), 1, 0.15, facecolor=color_bordillo, edgecolor=borde_general))
        if side == "Abajo":
            for x in range(cols):
                ax.add_patch(plt.Rectangle((x, -0.15), 1, 0.15, facecolor=color_bordillo, edgecolor=borde_general))
        if side == "Izquierda":
            for y in range(rows):
                ax.add_patch(plt.Rectangle((-0.15, y), 0.15, 1, facecolor=color_bordillo, edgecolor=borde_general))
        if side == "Derecha":
            for y in range(rows):
                ax.add_patch(plt.Rectangle((cols, y), 0.15, 1, facecolor=color_bordillo, edgecolor=borde_general))

if incluir_esquineros:
    s = 0.15
    for (cx, cy) in [(0,0), (0,rows), (cols,0), (cols,rows)]:
        ax.add_patch(plt.Rectangle((cx-s/2, cy-s/2), s, s, facecolor=color_bordillo, edgecolor=borde_general))

# Medidas reales con línea
largo_real = rows * 0.4 + 0.06 * (("Arriba" in pos_bord) + ("Abajo" in pos_bord)) if incluir_bordillos else rows * 0.4
ancho_real = cols * 0.4 + 0.06 * (("Izquierda" in pos_bord) + ("Derecha" in pos_bord)) if incluir_bordillos else cols * 0.4

ax.text(cols/2, rows + 0.6, f"{ancho_real:.2f} m", ha='center', va='bottom', fontsize=10)
ax.text(cols + 0.6, rows/2, f"{largo_real:.2f} m", ha='left', va='center', rotation=90, fontsize=10)
ax.plot([0, cols], [rows + 0.5, rows + 0.5], color="#666666")
ax.plot([cols + 0.5, cols + 0.5], [0, rows], color="#666666")

ax.set_xlim(-0.5, cols + 1.5)
ax.set_ylim(-0.5, rows + 1.5)
ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)
