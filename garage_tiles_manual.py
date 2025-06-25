import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="centered")
st.title("Piso Garage – Calculadora V2 (Modelos adaptativos)")

# ── 1. Medidas ──────────────────────────────────────────────────────────────
unidad = st.selectbox("Unidad", ["metros", "centímetros"])
factor = 1 if unidad == "metros" else 0.01
min_val = 1.0 if unidad == "metros" else 10.0

ancho_in  = st.number_input("Ancho",  min_value=min_val, value=4.0 if unidad=="metros" else 400.0, step=1.0)
largo_in  = st.number_input("Largo",  min_value=min_val, value=6.0 if unidad=="metros" else 600.0, step=1.0)

ancho_m, largo_m = ancho_in*factor, largo_in*factor
st.markdown(f"**Área:** {round(ancho_m*largo_m,2)} m²")

# ── 2. Bordillos / esquineros ───────────────────────────────────────────────
incluir_bordillos  = st.checkbox("Bordillos",  value=True)
incluir_esquineros = st.checkbox("Esquineros", value=True)
pos_bord = st.multiselect("Lados con bordillo", ["Arriba","Abajo","Izquierda","Derecha"],
                          default=["Arriba","Abajo","Izquierda","Derecha"])

# ── 3. Colores ──────────────────────────────────────────────────────────────
colores = {
    "Blanco":"#FFFFFF","Negro":"#000000","Gris":"#B0B0B0","Gris Oscuro":"#4F4F4F",
    "Azul":"#0070C0","Celeste":"#00B0F0","Amarillo":"#FFFF00","Verde":"#00B050","Rojo":"#FF0000"
}
lista = list(colores)
color_base       = st.selectbox("Color base",       lista, index=lista.index("Gris"))
color_secundario = st.selectbox("Color secundario", lista, index=lista.index("Rojo"))

# ── 4. Grilla ───────────────────────────────────────────────────────────────
cols = math.ceil(ancho_m/0.4)
rows = math.ceil(largo_m/0.4)

if "df" not in st.session_state or st.session_state.df.shape!=(rows,cols):
    st.session_state.df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

# ── 5. Modelos ──────────────────────────────────────────────────────────────
modelo = st.selectbox(
    "Modelo de diseño",
    [
        "MODELO A – Marco exterior",
        "MODELO B – Doble marco",
        "MODELO C – Cuadro central adaptable",
        "MODELO D – Ajedrez",
        "MODELO E – Diagonales",
        "MODELO F – Banda vertical + bordes",
        "MODELO G – Cruz central adaptable"
    ]
)

def centrales(n):
    """Devuelve la/s columna/s o fila/s centrales según paridad."""
    return [n//2] if n%2 else [n//2-1, n//2]

def aplicar_modelo():
    df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

    # columnas/filas centrales adaptativas
    c_cols = centrales(cols)
    c_rows = centrales(rows)

    if modelo.startswith("MODELO A"):
        m = max(1, min(rows,cols)//5)
        for y in range(rows):
            for x in range(cols):
                if x in (m, cols-m-1) or y in (m, rows-m-1):
                    df.iat[y,x]=color_secundario

    elif modelo.startswith("MODELO B"):
        for y in range(rows):
            for x in range(cols):
                if (x in (0,cols-1) or y in (0,rows-1)) or (x in (1,cols-2) or y in (1,rows-2)):
                    df.iat[y,x]=color_secundario

    elif modelo.startswith("MODELO C"):                 # cuadro central adaptable
        for y in c_rows:
            for x in c_cols: df.iat[y,x]=color_secundario
        # rodear el bloque central con un marco fino
        for y in c_rows:
            for x in range(cols): df.iat[y,x]=color_secundario
        for x in c_cols:
            for y in range(rows): df.iat[y,x]=color_secundario

    elif modelo.startswith("MODELO D"):                 # ajedrez
        for y in range(rows):
            for x in range(cols):
                if (x+y)%2==0: df.iat[y,x]=color_secundario

    elif modelo.startswith("MODELO E"):                 # diagonales completas
        for y in range(rows):
            left  = int(round(y*cols/rows))
            right = cols-1-int(round(y*cols/rows))
            df.iat[y,left]=color_secundario
            df.iat[y,right]=color_secundario

    elif modelo.startswith("MODELO F"):                 # banda vertical + bordes horiz.
        for x in c_cols:
            for y in range(rows): df.iat[y,x]=color_secundario
        for x in range(cols):
            df.iat[0,x]=df.iat[rows-1,x]=color_secundario

    elif modelo.startswith("MODELO G"):                 # cruz completa adaptativa
        for y in range(rows):
            for x in c_cols: df.iat[y,x]=color_secundario
        for x in range(cols):
            for y in c_rows: df.iat[y,x]=color_secundario

    st.session_state.df = df

if st.button("Aplicar modelo"):
    aplicar_modelo()

df = st.session_state.df

# ── 6. Conteo de piezas ─────────────────────────────────────────────────────
palmetas_color = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).to_dict()
bordillos = sum(cols if s in ("Arriba","Abajo") else rows for s in pos_bord) if incluir_bordillos else 0
esquineros = 4 if incluir_esquineros else 0

st.markdown("### Cantidad necesaria:")
for col, cnt in palmetas_color.items():
    st.markdown(f"- **{col}:** {cnt}")
st.markdown(f"- **Bordillos:** {bordillos}")
st.markdown(f"- **Esquineros:** {esquineros}")

# ── 7. Dibujo ───────────────────────────────────────────────────────────────
bord = "#FFFFFF" if color_base=="Negro" else "#000000"
fig, ax = plt.subplots(figsize=(cols/2, rows/2))
for y in range(rows):
    for x in range(cols):
        ax.add_patch(plt.Rectangle((x, rows-1-y),1,1,facecolor=colores[df.iat[y,x]],edgecolor=bord,linewidth=0.8))

bordillo_col="#000000"
if incluir_bordillos:
    if "Arriba" in pos_bord:    [ax.add_patch(plt.Rectangle((x,rows),1,0.15,facecolor=bordillo_col,edgecolor=bord)) for x in range(cols)]
    if "Abajo" in pos_bord:     [ax.add_patch(plt.Rectangle((x,-0.15),1,0.15,facecolor=bordillo_col,edgecolor=bord)) for x in range(cols)]
    if "Izquierda" in pos_bord: [ax.add_patch(plt.Rectangle((-0.15,y),0.15,1,facecolor=bordillo_col,edgecolor=bord)) for y in range(rows)]
    if "Derecha" in pos_bord:   [ax.add_patch(plt.Rectangle((cols,y),0.15,1,facecolor=bordillo_col,edgecolor=bord)) for y in range(rows)]

if incluir_esquineros:
    s=0.15
    for (cx,cy) in [(0,0),(0,rows),(cols,0),(cols,rows)]:
        ax.add_patch(plt.Rectangle((cx-s/2,cy-s/2),s,s,facecolor=bordillo_col,edgecolor=bord))

# Medidas reales
l_real = rows*0.4 + 0.06*((("Arriba" in pos_bord)+("Abajo" in pos_bord)) if incluir_bordillos else 0)
a_real = cols*0.4 + 0.06*((("Izquierda" in pos_bord)+("Derecha" in pos_bord)) if incluir_bordillos else 0)
ax.text(cols/2, rows+0.6, f"{a_real:.2f} m", ha="center", va="bottom")
ax.text(cols+0.6, rows/2, f"{l_real:.2f} m", ha="left", va="center", rotation=90)
ax.plot([0,cols],[rows+0.5,rows+0.5],color="#666")
ax.plot([cols+0.5,cols+0.5],[0,rows],color="#666")

ax.set_xlim(-0.5, cols+1.5)
ax.set_ylim(-0.5, rows+1.5)
ax.set_aspect('equal'); ax.axis('off')
st.pyplot(fig)
