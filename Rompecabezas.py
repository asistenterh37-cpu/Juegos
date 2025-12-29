import streamlit as st
import random
import time
import string

st.set_page_config(
    page_title="Rompecabezas PRO",
    layout="wide"
)

# ================== CSS RESPONSIVO ==================
st.markdown("""
<style>
.block-container { padding-top: 2rem; }

.tablero {
  display: grid;
  grid-template-columns: repeat(var(--n), 1fr);
  gap: 10px;
  max-width: 420px;
  margin: auto;
}

.tile {
  height: 70px;
  border-radius: 14px;
  border: 1px solid #ccc;
  font-size: 22px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  text-decoration: none;
  color: black;
}

.tile.empty {
  background: #f2f2f2;
  border-style: dashed;
}

@media (max-width: 600px) {
  .tablero { max-width: 320px; }
  .tile { height: 55px; font-size: 18px; }
}
</style>
""", unsafe_allow_html=True)

# ================== UTILIDADES ==================
def tiempo():
    return int(time.time())

def formato(seg):
    return f"{seg//60:02d}:{seg%60:02d}"

# ================== DESLIZANTE ==================
def tablero_resuelto(n):
    return list(range(1, n*n)) + [0]

def mezclar(tablero, n, pasos=200):
    b = tablero[:]
    for _ in range(pasos):
        i = b.index(0)
        r, c = divmod(i, n)
        vecinos = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            rr, cc = r+dr, c+dc
            if 0 <= rr < n and 0 <= cc < n:
                vecinos.append(rr*n+cc)
        j = random.choice(vecinos)
        b[i], b[j] = b[j], b[i]
    return b

def iniciar_deslizante(n):
    st.session_state.n = n
    st.session_state.tablero = mezclar(tablero_resuelto(n), n)
    st.session_state.mov = 0
    st.session_state.inicio = tiempo()

def render_deslizante():
    n = {"bajo":3,"medio":4,"alto":5}[st.session_state.dificultad]

    if "tablero" not in st.session_state or st.session_state.n != n:
        iniciar_deslizante(n)

    if "move" in st.query_params:
        i = int(st.query_params["move"])
        b = st.session_state.tablero
        z = b.index(0)
        r1,c1 = divmod(i,n)
        r2,c2 = divmod(z,n)
        if abs(r1-r2)+abs(c1-c2)==1:
            b[i],b[z]=b[z],b[i]
            st.session_state.mov += 1
        st.query_params.clear()
        st.rerun()

    col1,col2,col3,col4 = st.columns(4)
    if col1.button("🆕 Nuevo"): iniciar_deslizante(n)
    if col2.button("🔁 Reiniciar"): iniciar_deslizante(n)
    if col3.button("📘 Instrucciones"):
        st.info("Toca una ficha junto al espacio vacío.")
    if col4.button("✅ Resolver"):
        st.session_state.tablero = tablero_resuelto(n)

    st.markdown(
        f"Movimientos: {st.session_state.mov} | ⏱ {formato(tiempo()-st.session_state.inicio)}"
    )

    html = [f"<div class='tablero' style='--n:{n}'>"]
    for i,v in enumerate(st.session_state.tablero):
        if v==0:
            html.append("<div class='tile empty'></div>")
        else:
            html.append(f"<a class='tile' href='?move={i}'>{v}</a>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

# ================== APP ==================
st.title("🧩 Rompecabezas PRO")
st.caption("Elaborado por Soamy Lanza")

st.session_state.tipo = st.selectbox(
    "Tipo", ["Deslizante"]
)

st.session_state.dificultad = st.selectbox(
    "Dificultad", ["bajo","medio","alto"]
)

st.divider()
render_deslizante()

st.caption("© Rompecabezas PRO — Elaborado por Soamy Lanza")
