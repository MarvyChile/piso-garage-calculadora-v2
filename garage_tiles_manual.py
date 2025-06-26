# ──────────────────────────  Piso Garage – Calculadora V2  ──────────────────────────
# Modelos A–G + Canvas manual con cuadrícula (funciona en Streamlit < 1.26).
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

# ╭─ Parche image_to_url para versions antiguas de Streamlit ───────────╮
import streamlit.elements.image as _st_img
def _safe_image_to_url(img, width=None, clamp=False,
                       channels="RGB", output_format="PNG", filename="img"):
    buf = io.BytesIO()
    img.save(buf, format=output_format)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/{output_format.lower()};base64,{b64}"
if not hasattr(_st_img, "image_to_url") or "streamlit.elements" in str(_st_img.image_to_url):
    _st_img.image_to_url = _safe_image_to_url
# ╰─────────────────────────────────────────────────────────────────────╯

st.set_page_config(layout="centered")
st.title("Piso Garage – Calculadora V2  •  Diseño manual 2.0")

# ───────── 1. Medidas ─────────────────────────────────────────────────
unidad  = st.selectbox("Unidad", ["metros", "centímetros"])
factor  = 1 if unidad == "metros" else 0.01
min_val = 1.0 if unidad == "metros" else 10.0

ancho_in = st.number_input("Ancho", min_value=min_val,
                           value=4.0 if unidad=="metros" else 400.0)
largo_in = st.number_input("Largo", min_value=min_val,
                           value=6.0 if unidad=="metros" else 600.0)

ancho_m, largo_m = ancho_in*factor, largo_in*factor
st.markdown(f"**Área:** {round(ancho_m*largo_m,2)} m²")

# ───────── 2. Bordillos / esquineros ──────────────────────────────────
incluir_bordillos  = st.checkbox("Bordillos",  value=True)
incluir_esquineros = st.checkbox("Esquineros", value=True)
pos_bord = st.multiselect(
    "Lados con bordillo",
    ["Arriba", "Abajo", "Izquierda", "Derecha"],
    default=["Arriba", "Abajo", "Izquierda", "Derecha"]
)

# ───────── 3. Colores ────────────────────────────────────────────────
colores = {
    "Blanco": "#FFFFFF", "Negro": "#000000", "Gris": "#B0B0B0",
    "Gris Oscuro": "#4F4F4F", "Azul": "#0070C0", "Celeste": "#00B0F0",
    "Amarillo": "#FFFF00", "Verde": "#00B050", "Rojo": "#FF0000"
}
lista = list(colores)
c_base = st.selectbox("Color base", lista, index=lista.index("Gris"))
c_sec  = st.selectbox("Color secundario", lista, index=lista.index("Rojo"))

# ───────── 4. Dimensiones grilla ─────────────────────────────────────
cols = math.ceil(ancho_m / 0.4)
rows = math.ceil(largo_m / 0.4)

if "df" not in st.session_state or st.session_state.df.shape != (rows, cols):
    st.session_state.df = pd.DataFrame([[c_base]*cols for _ in range(rows)])

def centrales(n):
    return [n//2] if n % 2 else [n//2 - 1, n//2]

# ───────── 5. Modelos automáticos ────────────────────────────────────
modelo = st.selectbox(
    "Modelo automático",
    ["A – Marco", "B – Doble marco", "C – Cuadro",
     "D – Ajedrez", "E – Diagonales", "F – Banda+bordes", "G – Cruz"]
)

def aplicar_modelo():
    df = pd.DataFrame([[c_base]*cols for _ in range(rows)])
    cc, cr = centrales(cols), centrales(rows)

    if modelo.startswith("A"):
        m = max(1, min(rows, cols) // 5)
        for y in range(rows):
            for x in range(cols):
                if x in (m, cols-m-1) or y in (m, rows-m-1):
                    df.iat[y, x] = c_sec
    elif modelo.startswith("B"):
        for y in range(rows):
            for x in range(cols):
                if (x in (0, cols-1) or y in (0, rows-1)) \
                   or (x in (1, cols-2) or y in (1, rows-2)):
                    df.iat[y, x] = c_sec
    elif modelo.startswith("C"):
        for y in cr:
            for x in cc:
                df.iat[y, x] = c_sec
    elif modelo.startswith("D"):
        for y in range(rows):
            for x in range(cols):
                if (x + y) % 2 == 0:
                    df.iat[y, x] = c_sec
    elif modelo.startswith("E"):
        for y in range(rows):
            for x in range(cols):
                if x == y or x == cols - y - 1:
                    df.iat[y, x] = c_sec
    elif modelo.startswith("F"):
        for x in range(cols):
            df.iat[0, x] = df.iat[rows-1, x] = c_sec
        for y in range(rows):
            for x in cc:
                df.iat[y, x] = c_sec
    elif modelo.startswith("G"):
        for y in range(rows):
            for x in cc:
                df.iat[y, x] = c_sec
        for x in range(cols):
            for y in cr:
                df.iat[y, x] = c_sec

    st.session_state.df = df

if st.button("Aplicar modelo automático"):
    aplicar_modelo()

# ───────── 6. Diseño manual con canvas ───────────────────────────────
st.markdown("### Diseño manual (clic en celdas)")
if st.checkbox("Activar diseño manual"):
    color_sel = st.radio("Color", lista, horizontal=True, key="paleta")
    cell = 40
    # Cuadrícula
    img = Image.new("RGB", (cols*cell, rows*cell), "white")
    draw = ImageDraw.Draw(img)
    for x in range(cols+1):
        draw.line([(x*cell, 0), (x*cell, rows*cell)], fill="#CCCCCC")
    for y in range(rows+1):
        draw.line([(0, y*cell), (cols*cell, y*cell)], fill="#CCCCCC")

    canvas = st_canvas(
        fill_color=colores[color_sel],
        stroke_width=0,
        background_image=img,
        height=rows*cell,
        width=cols*cell,
        drawing_mode="point",
        update_streamlit=True
    )

    if st.button("Guardar diseño manual"):
        if canvas.json_data and "objects" in canvas.json_data:
            for o in canvas.json_data["objects"]:
                x = int(o["left"] // cell)
                y = int(o["top"]  // cell)
                if 0 <= x < cols and 0 <= y < rows:
                    st.session_state.df.iat[rows-1-y, x] = color_sel

df = st.session_state.df  # Grilla final

# ───────── 7. Conteo de piezas ───────────────────────────────────────
palmetas = df.apply(pd.Series.value_counts).fillna(0) \
             .sum(axis=1).astype(int).to_dict()
bordillos = sum(cols if s in ("Arriba", "Abajo") else rows for s in pos_bord) \
            if incluir_bordillos else 0
esquineros = 4 if incluir_esquineros else 0

st.markdown("### Cantidad necesaria:")
for col, n in palmetas.items():
    st.markdown(f"- **{col}:** {n}")
st.markdown(f"- **Bordillos:** {bordillos}")
st.markdown(f"- **Esquineros:** {esquineros}")

# ───────── 8. Dibujo final ────────────────────────────────────────────
bordec = "#FFFFFF" if c_base == "Negro" else "#000000"
fig, ax = plt.subplots(figsize=(cols/2, rows/2))
for y in range(rows):
    for x in range(cols):
        ax.add_patch(
            plt.Rectangle(
                (x, rows-1-y), 1, 1,
                facecolor=colores[df.iat[y, x]],
                edgecolor=bordec, lw=0.8
            )
        )

# Bordillos
bord_col = "#000000"
if incluir_bordillos:
    if "Arriba" in pos_bord:
        for x in range(cols):
            ax.add_patch(
                plt.Rectangle((x, rows), 1, .15,
                              facecolor=bord_col, edgecolor=bordec)
            )
    if "Abajo" in pos_bord:
        for x in range(cols):
            ax.add_patch(
                plt.Rectangle((x, -.15), 1, .15,
                              facecolor=bord_col, edgecolor=bordec)
            )
    if "Izquierda" in pos_bord:
        for y in range(rows):
            ax.add_patch(
                plt.Rectangle((-.15, y), .15, 1,
                              facecolor=bord_col, edgecolor=bordec)
            )
    if "Derecha" in pos_bord:
        for y in range(rows):
            ax.add_patch(
                plt.Rectangle((cols, y), .15, 1,
                              facecolor=bord_col, edgecolor=bordec)
            )

# Esquineros
if incluir_esquineros:
    s = .15
    for cx, cy in [(0, 0), (0, rows), (cols, 0), (cols, rows)]:
        ax.add_patch(
            plt.Rectangle((cx-s/2, cy-s/2), s, s,
                          facecolor=bord_col, edgecolor=bordec)
        )

# Medidas reales
l_real = rows*0.4 + 0.06*((("Arriba" in pos_bord) + ("Abajo" in pos_bord))
                           if incluir_bordillos else 0)
a_real = cols*0.4 + 0.06*((("Izquierda" in pos_bord) + ("Derecha" in pos_bord))
                           if incluir_bordillos else 0)

# Etiquetas de medida
ax.text(
    cols/2, rows + 0.6,
    f"{a_real:.2f} m", ha="center", va="bottom"
)
ax.text(
    cols + 0.6, rows/2,
    f"{l_real:.2f} m", ha="left", va="center", rotation=90
)

# Líneas guía
ax.plot([0, cols], [rows + 0.5, rows + 0.5], color="#666")
ax.plot([cols + 0.5, cols + 0.5], [0, rows], color="#666")

# Ajustes finales
ax.set_xlim(-0.5, cols + 1.5)
ax.set_ylim(-0.5, rows + 1.5)
ax.set_aspect("equal")
ax.axis("off")
st.pyplot(fig)
