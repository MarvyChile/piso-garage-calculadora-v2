import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="centered")
st.title("Piso Garage - Calculadora V2")

# Unidad y dimensiones
unidad = st.selectbox("Selecciona la unidad de medida", ["metros", "centímetros"])
factor = 1 if unidad == "metros" else 0.01
min_val = 1.0 if unidad == "metros" else 10.0

ancho_input = st.number_input("Ancho del espacio", min_value=min_val,
                              value=4.0 if unidad == "metros" else 400.0, step=1.0)
largo_input = st.number_input("Largo del espacio", min_value=min_val,
                              value=6.0 if unidad == "metros" else 600.0, step=1.0)

ancho_m, largo_m = ancho_input * factor, largo_input * factor
st.markdown(f"**Área total:** {round(ancho_m * largo_m, 2)} m²")

# Bordillos y esquineros
incluir_bordillos = st.checkbox("Agregar bordillos", value=True)
incluir_esquineros = st.checkbox("Agregar esquineros", value=True)
pos_bord = st.multiselect("¿Dónde colocar bordillos?",
                          ["Arriba", "Abajo", "Izquierda", "Derecha"],
                          default=["Arriba", "Abajo", "Izquierda", "Derecha"])

# Colores
colores = {
    "Blanco": "#FFFFFF", "Negro": "#000000", "Gris": "#B0B0B0", "Gris Oscuro": "#4F4F4F",
    "Azul": "#0070C0", "Celeste": "#00B0F0", "Amarillo": "#FFFF00",
    "Verde": "#00B050", "Rojo": "#FF0000"
}
lista_colores = list(colores.keys())
color_base = st.selectbox("Color base", lista_colores, index=lista_colores.index("Gris"))
color_secundario = st.selectbox("Color secundario", lista_colores, index=lista_colores.index("Rojo"))

# Grilla
cols, rows = math.ceil(ancho_m / 0.4), math.ceil(largo_m / 0.4)
if 'df' not in st.session_state or st.session_state.df.shape != (rows, cols):
    st.session_state.df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

# Modelos A‑G
modelo = st.selectbox(
    "Modelo de diseño",
    [
        "MODELO A – Marco exterior",
        "MODELO B – Doble marco",
        "MODELO C – Cuadro central",
        "MODELO D – Ajedrez",
        "MODELO E – Diagonales",
        "MODELO F – Banda vertical + bordes horiz.",
        "MODELO G – Cruz central"
    ]
)

def aplicar_modelo():
    df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

    if modelo.startswith("MODELO A"):
        m = max(1, min(rows, cols)//5)
        for y in range(rows):
            for x in range(cols):
                if x in (m, cols-m-1) or y in (m, rows-m-1):
                    df.iat[y,x] = color_secundario
    elif modelo.startswith("MODELO B"):
        for y in range(rows):
            for x in range(cols):
                if (x in (0, cols-1) or y in (0, rows-1)) or (x in (1, cols-2) or y in (1, rows-2)):
                    df.iat[y,x] = color_secundario
    elif modelo.startswith("MODELO C"):
        cx, cy = cols//2, rows//2
        for y in range(cy-1, cy+2):
            for x in range(cx-1, cx+2):
                if 0<=y<rows and 0<=x<cols:
                    df.iat[y,x] = color_secundario
    elif modelo.startswith("MODELO D"):
        for y in range(rows):
            for x in range(cols):
                if (x+y)%2==0:
                    df.iat[y,x] = color_secundario
    elif modelo.startswith("MODELO E"):
        for y in range(rows):
            for x in range(cols):
                if x==y or x==cols-y-1:
                    df.iat[y,x] = color_secundario
    elif modelo.startswith("MODELO F"):
        for x in range(cols):
            df.iat[0,x]=df.iat[rows-1,x]=color_secundario
        for y in range(rows):
            df.iat[y,cols//2]=color_secundario
    elif modelo.startswith("MODELO G"):
        for y in range(rows):
            df.iat[y,cols//2]=color_secundario
        for x in range(cols):
            df.iat[rows//2,x]=color_secundario

    st.session_state.df = df

if st.button("Aplicar modelo"):
    aplicar_modelo()

df = st.session_state.df

# Contar piezas
palmetas_color = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).to_dict()
bordillos = sum(cols if s in ["Arriba","Abajo"] else rows for s in pos_bord) if incluir_bordillos else 0
esquineros = 4 if incluir_esquineros else 0

st.markdown("### Cantidad necesaria:")
for col, cnt in palmetas_color.items():
    st.markdown(f"- **{col}:** {cnt}")
st.markdown(f"- **Bordillos:** {bordillos}")
st.markdown(f"- **Esquineros:** {esquineros}")

# Dibujar
borde = "#FFFFFF" if color_base=="Negro" else "#000000"
fig, ax = plt.subplots(figsize=(cols/2, rows/2))
for y in range(rows):
    for x in range(cols):
        ax.add_patch(plt.Rectangle((x,rows-1-y),1,1,facecolor=colores[df.iat[y,x]],edgecolor=borde,linewidth=0.8))

# Bordillos
col_bord="#000000"
if incluir_bordillos:
    if "Arriba" in pos_bord:
        for x in range(cols): ax.add_patch(plt.Rectangle((x,rows),1,0.15,facecolor=col_bord,edgecolor=borde))
    if "Abajo" in pos_bord:
        for x in range(cols): ax.add_patch(plt.Rectangle((x,-0.15),1,0.15,facecolor=col_bord,edgecolor=borde))
    if "Izquierda" in pos_bord:
        for y in range(rows): ax.add_patch(plt.Rectangle((-0.15,y),0.15,1,facecolor=col_bord,edgecolor=borde))
    if "Derecha" in pos_bord:
        for y in range(rows): ax.add_patch(plt.Rectangle((cols,y),0.15,1,facecolor=col_bord,edgecolor=borde))

if incluir_esquineros:
    s=0.15
    for (cx,cy) in [(0,0),(0,rows),(cols,0),(cols,rows)]:
        ax.add_patch(plt.Rectangle((cx-s/2,cy-s/2),s,s,facecolor=col_bord,edgecolor=borde))

# Medidas reales
l_real = rows*0.4 + (0.06 if incluir_bordillos and "Arriba" in pos_bord else 0) + (0.06 if incluir_bordillos and "Abajo" in pos_bord else 0)
a_real = cols*0.4 + (0.06 if incluir_bordillos and "Izquierda" in pos_bord else 0) + (0.06 if incluir_bordillos and "Derecha" in pos_bord else 0)
ax.text(cols/2, rows+0.6, f"{a_real:.2f} m", ha="center", va="bottom")
ax.text(cols+0.6, rows/2, f"{l_real:.2f} m", ha="left", va="center", rotation=90)
ax.plot([0,cols],[rows+0.5,rows+0.5], color="#666")
ax.plot([cols+0.5,cols+0.5],[0,rows], color="#666")

ax.set_xlim(-0.5, cols+1.5); ax.set_ylim(-0.5, rows+1.5)
ax.set_aspect('equal'); ax.axis('off')
st.pyplot(fig)
