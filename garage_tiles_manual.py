import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

# ── Config ───────────────────────────────────────────────
st.set_page_config(layout="centered")
st.title("Piso Garage – Calculadora V2  +  Diseño manual")

# ── 1. Medidas ───────────────────────────────────────────
unidad  = st.selectbox("Unidad", ["metros", "centímetros"])
factor  = 1 if unidad == "metros" else 0.01
min_val = 1.0 if unidad == "metros" else 10.0

ancho_in = st.number_input("Ancho",  min_value=min_val,
                           value=4.0 if unidad=="metros" else 400.0, step=1.0)
largo_in = st.number_input("Largo",  min_value=min_val,
                           value=6.0 if unidad=="metros" else 600.0, step=1.0)

ancho_m, largo_m = ancho_in*factor, largo_in*factor
st.markdown(f"**Área:** {round(ancho_m*largo_m,2)} m²")

# ── 2. Bordillos / esquineros ────────────────────────────
incluir_bordillos  = st.checkbox("Bordillos",  value=True)
incluir_esquineros = st.checkbox("Esquineros", value=True)
pos_bord = st.multiselect("Lados con bordillo",
                          ["Arriba","Abajo","Izquierda","Derecha"],
                          default=["Arriba","Abajo","Izquierda","Derecha"])

# ── 3. Colores ───────────────────────────────────────────
colores = {
    "Blanco":"#FFFFFF","Negro":"#000000","Gris":"#B0B0B0","Gris Oscuro":"#4F4F4F",
    "Azul":"#0070C0","Celeste":"#00B0F0","Amarillo":"#FFFF00","Verde":"#00B050","Rojo":"#FF0000"
}
lista = list(colores)
color_base = st.selectbox("Color base", lista, index=lista.index("Gris"))
color_sec  = st.selectbox("Color secundario", lista, index=lista.index("Rojo"))

# ── 4. Grilla ────────────────────────────────────────────
cols = math.ceil(ancho_m/0.4)
rows = math.ceil(largo_m/0.4)

if "df" not in st.session_state or st.session_state.df.shape != (rows, cols):
    st.session_state.df = pd.DataFrame([[color_base]*cols for _ in range(rows)])

def centrales(n): return [n//2] if n%2 else [n//2-1, n//2]

# ── 5. Modelos automáticos ───────────────────────────────
modelo = st.selectbox(
    "Modelo automático",
    ["A – Marco", "B – Doble marco", "C – Cuadro central",
     "D – Ajedrez", "E – Diagonales", "F – Banda+bordes", "G – Cruz"]
)

def aplicar_modelo():
    df = pd.DataFrame([[color_base]*cols for _ in range(rows)])
    c_cols, c_rows = centrales(cols), centrales(rows)

    if modelo.startswith("A"):
        m = max(1, min(rows, cols)//5)
        for y in range(rows):
            for x in range(cols):
                if x in (m, cols-m-1) or y in (m, rows-m-1):
                    df.iat[y,x]=color_sec
    elif modelo.startswith("B"):
        for y in range(rows):
            for x in range(cols):
                if (x in (0,cols-1) or y in (0,rows-1)) or (x in (1,cols-2) or y in (1,rows-2)):
                    df.iat[y,x]=color_sec
    elif modelo.startswith("C"):
        for y in c_rows:
            for x in c_cols: df.iat[y,x]=color_sec
    elif modelo.startswith("D"):
        for y in range(rows):
            for x in range(cols):
                if (x+y)%2==0: df.iat[y,x]=color_sec
    elif modelo.startswith("E"):
        for y in range(rows):
            for x in range(cols):
                if x==y or x==cols-y-1: df.iat[y,x]=color_sec
    elif modelo.startswith("F"):
        for x in range(cols): df.iat[0,x]=df.iat[rows-1,x]=color_sec
        for y in range(rows):
            for x in c_cols: df.iat[y,x]=color_sec
    elif modelo.startswith("G"):
        for x in range(cols):
            for y in centrales(rows): df.iat[y,x]=color_sec
        for y in range(rows):
            for x in centrales(cols): df.iat[y,x]=color_sec

    st.session_state.df = df

if st.button("Aplicar modelo automático"):
    aplicar_modelo()

# ── 6. Panel de diseño manual ────────────────────────────
st.markdown("### Diseño manual")
activar_manual = st.checkbox("Activar diseño manual")

if activar_manual:
    # Editor de datos con dropdown por celda
    column_config = {
        str(i): st.column_config.SelectboxColumn("",
                    options=lista,
                    required=True) for i in range(cols)
    }
    edited = st.data_editor(
        st.session_state.df.copy(),
        column_config=column_config,
        disabled=False,
        hide_index=True,
        key="editor"
    )

    if st.button("Aplicar diseño manual"):
        st.session_state.df = edited.copy()

df = st.session_state.df

# ── 7. Conteo de piezas ──────────────────────────────────
palmetas = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).to_dict()
bordillos = (sum(cols if s in ("Arriba","Abajo") else rows for s in pos_bord)
             if incluir_bordillos else 0)
esquineros = 4 if incluir_esquineros else 0

st.markdown("### Cantidad necesaria:")
for c, n in palmetas.items():
    st.markdown(f"- **{c}:** {n}")
st.markdown(f"- **Bordillos:** {bordillos}")
st.markdown(f"- **Esquineros:** {esquineros}")

# ── 8. Dibujo ────────────────────────────────────────────
bordec = "#FFFFFF" if color_base=="Negro" else "#000000"
fig, ax = plt.subplots(figsize=(cols/2, rows/2))

for y in range(rows):
    for x in range(cols):
        ax.add_patch(plt.Rectangle((x,rows-1-y),1,1,
                                   facecolor=colores[df.iat[y,x]],
                                   edgecolor=bordec,lw=0.8))

# Bordillos (bucles)
bord_col="#000000"
if incluir_bordillos:
    if "Arriba"   in pos_bord:
        for x in range(cols):
            ax.add_patch(plt.Rectangle((x,rows),1,.15,facecolor=bord_col,edgecolor=bordec))
    if "Abajo"    in pos_bord:
        for x in range(cols):
            ax.add_patch(plt.Rectangle((x,-.15),1,.15,facecolor=bord_col,edgecolor=bordec))
    if "Izquierda" in pos_bord:
        for y in range(rows):
            ax.add_patch(plt.Rectangle((-.15,y),.15,1,facecolor=bord_col,edgecolor=bordec))
    if "Derecha"  in pos_bord:
        for y in range(rows):
            ax.add_patch(plt.Rectangle((cols,y),.15,1,facecolor=bord_col,edgecolor=bordec))

# Esquineros
if incluir_esquineros:
    s=.15
    for cx,cy in [(0,0),(0,rows),(cols,0),(cols,rows)]:
        ax.add_patch(plt.Rectangle((cx-s/2,cy-s/2),s,s,facecolor=bord_col,edgecolor=bordec))

# Medidas
l_real = rows*0.4 + 0.06*((("Arriba" in pos_bord)+("Abajo" in pos_bord)) if incluir_bordillos else 0)
a_real = cols*0.4 + 0.06*((("Izquierda" in pos_bord)+("Derecha" in pos_bord)) if incluir_bordillos else 0)
ax.text(cols/2, rows+.6, f"{a_real:.2f} m", ha="center", va="bottom")
ax.text(cols+.6, rows/2, f"{l_real:.2f} m", ha="left", va="center", rotation=90)

ax.plot([0,cols],[rows+.5,rows+.5],color="#666")
ax.plot([cols+.5,cols+.5],[0,rows],color="#666")
ax.set_xlim(-.5, cols+1.5); ax.set_ylim(-.5, rows+1.5)
ax.set_aspect("equal"); ax.axis("off")
st.pyplot(fig)
