# ──────────────────────────  Piso Garage – Calculadora V2  ──────────────────────────
#   • Modelos A–G
#   • Canvas manual con cuadrícula visible
#   • SIN errores (usa background_image_url)
# Requisitos:
#   streamlit>=1.18
#   streamlit-drawable-canvas
#   pandas, numpy, matplotlib, Pillow
# ─────────────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math, io, base64
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas

# ─── Util: PIL.Image → data-URL ───────────────────────────────────────
def img_to_dataurl(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

# ─── Interface ---------------------------------------------------------------------
st.set_page_config(layout="centered")
st.title("Piso Garage – Calculadora V2  •  Diseño manual 2.0")

unidad  = st.selectbox("Unidad", ["metros", "centímetros"])
factor  = 1 if unidad=="metros" else 0.01
ancho_in = st.number_input("Ancho", 1.0 if unidad=="metros" else 10.0, 4.0 if unidad=="metros" else 400.0)
largo_in = st.number_input("Largo", 1.0 if unidad=="metros" else 10.0, 6.0 if unidad=="metros" else 600.0)

ancho_m, largo_m = ancho_in*factor, largo_in*factor
st.markdown(f"**Área:** {round(ancho_m*largo_m,2)} m²")

incluir_bordillos  = st.checkbox("Bordillos",  True)
incluir_esquineros = st.checkbox("Esquineros", True)
pos_bord = st.multiselect("Lados con bordillo",
                          ["Arriba","Abajo","Izquierda","Derecha"],
                          default=["Arriba","Abajo","Izquierda","Derecha"])

colores = {
    "Blanco":"#FFFFFF","Negro":"#000000","Gris":"#B0B0B0","Gris Oscuro":"#4F4F4F",
    "Azul":"#0070C0","Celeste":"#00B0F0","Amarillo":"#FFFF00","Verde":"#00B050","Rojo":"#FF0000"}
lista = list(colores)
c_base = st.selectbox("Color base", lista, lista.index("Gris"))
c_sec  = st.selectbox("Color secundario", lista, lista.index("Rojo"))

# ─── Grilla ------------------------------------------------------------------------
cols = math.ceil(ancho_m/0.4)
rows = math.ceil(largo_m/0.4)
if "df" not in st.session_state or st.session_state.df.shape!=(rows,cols):
    st.session_state.df = pd.DataFrame([[c_base]*cols for _ in range(rows)])
df = st.session_state.df

# ─── Modelos automáticos ------------------------------------------------------------
modelo = st.selectbox("Modelo automático",
    ["A – Marco","B – Doble marco","C – Cuadro","D – Ajedrez",
     "E – Diagonales","F – Banda+bordes","G – Cruz"])

def cent(n): return [n//2] if n%2 else [n//2-1,n//2]

def aplicar_modelo():
    g = pd.DataFrame([[c_base]*cols for _ in range(rows)])
    cc, cr = cent(cols), cent(rows)
    if modelo.startswith("A"):
        m=max(1,min(rows,cols)//5)
        for y in range(rows):
            for x in range(cols):
                if x in (m,cols-m-1) or y in (m,rows-m-1): g.iat[y,x]=c_sec
    elif modelo.startswith("B"):
        for y in range(rows):
            for x in range(cols):
                if (x in (0,cols-1) or y in (0,rows-1)) or (x in (1,cols-2) or y in (1,rows-2)):
                    g.iat[y,x]=c_sec
    elif modelo.startswith("C"):
        for y in cr:
            for x in cc: g.iat[y,x]=c_sec
    elif modelo.startswith("D"):
        for y in range(rows):
            for x in range(cols):
                if (x+y)%2==0: g.iat[y,x]=c_sec
    elif modelo.startswith("E"):
        for y in range(rows):
            for x in range(cols):
                if x==y or x==cols-y-1: g.iat[y,x]=c_sec
    elif modelo.startswith("F"):
        for x in range(cols): g.iat[0,x]=g.iat[rows-1,x]=c_sec
        for y in range(rows):
            for x in cc: g.iat[y,x]=c_sec
    elif modelo.startswith("G"):
        for y in range(rows):
            for x in cc: g.iat[y,x]=c_sec
        for x in range(cols):
            for y in cr: g.iat[y,x]=c_sec
    st.session_state.df = g
    st.experimental_rerun()

if st.button("Aplicar modelo automático"): aplicar_modelo()

# ─── Canvas manual -----------------------------------------------------------------
st.markdown("### Diseño manual (clic en celdas)")
if st.checkbox("Activar diseño manual"):
    color_sel = st.radio("Color", lista, horizontal=True, key="paleta")
    cell=40
    img = Image.new("RGB",(cols*cell,rows*cell),"white")
    drw = ImageDraw.Draw(img); 
    for x in range(cols+1): drw.line([(x*cell,0),(x*cell,rows*cell)],fill="#CCCCCC")
    for y in range(rows+1): drw.line([(0,y*cell),(cols*cell,y*cell)],fill="#CCCCCC")
    data_url = img_to_dataurl(img)                                      # ← clave

    canvas = st_canvas(
        fill_color=colores[color_sel], stroke_width=0,
        background_image_url=data_url,            # ← usar URL, no objeto
        height=rows*cell, width=cols*cell,
        drawing_mode="point", update_streamlit=True)

    if st.button("Guardar diseño manual"):
        if canvas.json_data and "objects" in canvas.json_data:
            for o in canvas.json_data["objects"]:
                x=int(o["left"]//cell); y=int(o["top"]//cell)
                if 0<=x<cols and 0<=y<rows:
                    st.session_state.df.iat[rows-1-y,x]=color_sel
        st.experimental_rerun()

df = st.session_state.df

# ─── Conteo de piezas --------------------------------------------------------------
st.markdown("### Cantidad necesaria:")
cuenta = df.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int)
for col,n in cuenta.items(): st.markdown(f"- **{col}:** {n}")
bordillos = sum(cols if s in ("Arriba","Abajo") else rows for s in pos_bord) if incluir_bordillos else 0
esqs=4 if incluir_esquineros else 0
st.markdown(f"- **Bordillos:** {bordillos}")
st.markdown(f"- **Esquineros:** {esqs}")

# ─── Dibujo final ------------------------------------------------------------------
bordec = "#FFFFFF" if c_base=="Negro" else "#000000"
fig, ax = plt.subplots(figsize=(cols/2,rows/2))
for y in range(rows):
    for x in range(cols):
        ax.add_patch(plt.Rectangle((x,rows-1-y),1,1,facecolor=colores[df.iat[y,x]],edgecolor=bordec,lw=0.8))

# bordillos
bordc="#000"
if incluir_bordillos:
    if "Arriba" in pos_bord:
        for x in range(cols): ax.add_patch(plt.Rectangle((x,rows),1,.15,facecolor=bordc,edgecolor=bordec))
    if "Abajo" in pos_bord:
        for x in range(cols): ax.add_patch(plt.Rectangle((x,-.15),1,.15,facecolor=bordc,edgecolor=bordec))
    if "Izquierda" in pos_bord:
        for y in range(rows): ax.add_patch(plt.Rectangle((-.15,y),.15,1,facecolor=bordc,edgecolor=bordec))
    if "Derecha" in pos_bord:
        for y in range(rows): ax.add_patch(plt.Rectangle((cols,y),.15,1,facecolor=bordc,edgecolor=bordec))
if incluir_esquineros:
    s=.15
    for cx,cy in [(0,0),(0,rows),(cols,0),(cols,rows)]:
        ax.add_patch(plt.Rectangle((cx-s/2,cy-s/2),s,s,facecolor=bordc,edgecolor=bordec))

l_real = rows*0.4+0.06*((("Arriba" in pos_bord)+("Abajo" in pos_bord)) if incluir_bordillos else 0)
a_real = cols*0.4+0.06*((("Izquierda" in pos_bord)+("Derecha" in pos_bord)) if incluir_bordillos else 0)
ax.text(cols/2, rows+.6, f"{a_real:.2f} m", ha="center", va="bottom")
ax.text(cols+.6, rows/2, f"{l_real:.2f} m", ha="left", va="center", rotation=90)
ax.plot([0,cols],[rows+.5,rows+.5],color="#666")
ax.plot([cols+.5,cols+.5],[0,rows],color="#666")
ax.set_xlim(-.5, cols+1.5); ax.set_ylim(-.5, rows+1.5); ax.set_aspect("equal"); ax.axis("off")
st.pyplot(fig)
